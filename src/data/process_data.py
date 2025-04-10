import os
import math
import logging
import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from pathlib import Path
from datetime import timedelta

logging.basicConfig(level=logging.INFO)

# Definir la ruta raíz del proyecto (retroceder tres niveles desde src/data)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
STRUCTURE_FILE = ROOT_DIR / "data" / "raw" / "estructura.xlsx"
TABLA1_FILE = ROOT_DIR / "data" / "raw" / "tabla1.xlsx"
TABLA2_FILE = ROOT_DIR / "data" / "raw" / "tabla2.xlsx"

# Verificar que los archivos existan
for file in [STRUCTURE_FILE, TABLA1_FILE, TABLA2_FILE]:
    if not file.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file}")

# Cargar la estructura de los datos
ESTRUCTURA = pd.read_excel(STRUCTURE_FILE)

# Definir rutas de salida
REPORTS_PATH = ROOT_DIR / "reports"
REPORTS_PATH.mkdir(parents=True, exist_ok=True)

MAX_WORKERS = 4
HISTORIAL_BLOQUEO = defaultdict(set)

class ConciliadorAvanzado:
    def __init__(self):
        self.fase = 0
        self.iteracion = 0
        self.max_fases = 5
        self.umbrales = {
            'score_inicial': 85,
            'diferencia_fecha': 7,
            'tolerancia_importe': 0.05,
            'min_matches_por_fase': 10
        }
        self.historial_matches = pd.DataFrame()
        self.pesos_campos = self._inicializar_pesos()
        self.contador_segregados = 0

    def _inicializar_pesos(self):
        return {campo: 1.0 for campo in ESTRUCTURA[ESTRUCTURA['tipo'] == 'texto']['campo']}

    def _ajustar_umbrales(self):
        self.umbrales['score_inicial'] = max(70, 85 - self.fase * 3)
        self.umbrales['diferencia_fecha'] += 3 * self.fase
        self.umbrales['tolerancia_importe'] = min(0.15, 0.05 + 0.02 * self.fase)

    def cargar_datos(self):
        # Para tabla1, leemos normalmente
        tabla1 = pd.read_excel(TABLA1_FILE, dtype={'id': str, 'subid': str})
        # Para tabla2, si no existe "subid", lo agregamos con valor por defecto "1"
        tabla2 = pd.read_excel(TABLA2_FILE, dtype={'id': str})
        if "subid" not in tabla2.columns:
            tabla2["subid"] = "1"
        for df in [tabla1, tabla2]:
            df['match_valor'] = None
            df['match_score'] = 0
            df['conciliado'] = False
        return tabla1, tabla2

    def procesar_texto(self, df, campo):
        texto = df[campo].astype(str).str.lower()
        if ESTRUCTURA[ESTRUCTURA['campo'] == campo]['depurar'].iloc[0] == 'si':
            texto = texto.str.replace(r'[^\w\s]', '', regex=True)
            texto = texto.str.replace(r'\s+', ' ', regex=True).str.strip()
        return texto

    def generar_clave_compuesta(self, df):
        campos = ESTRUCTURA[ESTRUCTURA['similar'] == 'si']['campo'].tolist()
        print("Campos para clave compuesta:", campos)  # Depuración
        df['clave_compuesta'] = df[campos].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
        return df

    def _preprocesar_blocking(self, df, campo):
        df['block'] = df[campo].str[:4].fillna('')
        return df.groupby('block')[campo].apply(list).to_dict()

    def _match_semilla(self, tabla1, tabla2):
        tabla1 = self.generar_clave_compuesta(tabla1)
        tabla2 = self.generar_clave_compuesta(tabla2)
        merged = pd.merge(tabla1, tabla2, on='clave_compuesta', suffixes=('_1', '_2'))
        if not merged.empty:
            logging.info(f"Matches exactos encontrados: {len(merged)}")
            tabla1.loc[tabla1['clave_compuesta'].isin(merged['clave_compuesta']), 'match_valor'] = tabla1['clave_compuesta']
            tabla1.loc[tabla1['clave_compuesta'].isin(merged['clave_compuesta']), 'match_score'] = 100
            tabla1.loc[tabla1['clave_compuesta'].isin(merged['clave_compuesta']), 'conciliado'] = True
            tabla2.loc[tabla2['clave_compuesta'].isin(merged['clave_compuesta']), 'conciliado'] = True
        return tabla1, tabla2

    def matching_inteligente(self, tabla1, tabla2, campo):
        block_dict = self._preprocesar_blocking(tabla2, campo)
        valores_unicos = tabla1[campo].unique()
        
        def _match(valor):
            if valor in HISTORIAL_BLOQUEO[self.iteracion]:
                return (None, 0)
            block = valor[:4] if len(valor) >= 4 else valor
            opciones = [x for x in block_dict.get(block, []) if f"{x}-{valor}" not in HISTORIAL_BLOQUEO]
            if not opciones:
                return (None, 0)
            result = process.extractOne(valor, opciones, scorer=fuzz.token_sort_ratio,
                                        score_cutoff=self.umbrales['score_inicial'])
            return result if result else (None, 0)
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            resultados = dict(zip(valores_unicos, executor.map(_match, valores_unicos)))
        tabla1['match_valor'] = tabla1[campo].map(lambda x: resultados.get(x, (None, 0))[0])
        tabla1['match_score'] = tabla1[campo].map(lambda x: resultados.get(x, (None, 0))[1])
        return tabla1

    def segregar_registro(self, registro, tipo='tabla1', diferencia_importe=0):
        nuevo_registro = registro.copy()
        self.contador_segregados += 1
        if tipo == 'tabla1':
            registro['monto'] -= diferencia_importe
            nuevo_registro['monto'] = diferencia_importe
            nuevo_registro['subid'] = str(int(registro['subid']) + 1)
            nuevo_registro['segregable'] -= 1
        else:
            registro['monto'] = diferencia_importe
            nuevo_registro['monto'] -= diferencia_importe
            nuevo_registro['subid'] = str(int(registro['subid']) + 1)
            nuevo_registro['segregable'] -= 1
        return registro, nuevo_registro

    def _validar_matches(self, tabla1, tabla2):
        for col in ['id', 'subid']:
            tabla1[col] = tabla1[col].astype(str)
            tabla2[col] = tabla2[col].astype(str)
        tabla1['match_id'] = tabla1['match_valor'].apply(lambda x: x.split('-')[0] if pd.notna(x) and '-' in x else '')
        tabla1['match_subid'] = tabla1['match_valor'].apply(lambda x: x.split('-')[1] if pd.notna(x) and '-' in x else '')
        tabla2['match_id'] = tabla2['match_valor'].apply(lambda x: x.split('-')[0] if pd.notna(x) and '-' in x else '')
        tabla2['match_subid'] = tabla2['match_valor'].apply(lambda x: x.split('-')[1] if pd.notna(x) and '-' in x else '')
        for col in ['match_id', 'match_subid']:
            tabla1[col] = tabla1[col].astype(str)
            tabla2[col] = tabla2[col].astype(str)
        merged = pd.merge(tabla1, tabla2,
                          left_on=['match_id', 'match_subid'],
                          right_on=['id', 'subid'],
                          suffixes=('_1', '_2'))
        for col in ['fecha_1', 'fecha_2']:
            merged[col] = pd.to_datetime(merged[col], errors='coerce')
        mask = (
            (abs(merged['monto_1'] - merged['monto_2']) / merged['monto_2'] > self.umbrales['tolerancia_importe']) |
            (abs((merged['fecha_1'] - merged['fecha_2']).dt.days) > self.umbrales['diferencia_fecha'])
        )
        no_conflictivos = merged[~mask]
        cols_t1 = [col for col in tabla1.columns if col in merged.columns]
        cols_t2 = [col for col in tabla2.columns if col in merged.columns]
        tabla1_actualizada = pd.concat([
            no_conflictivos[cols_t1].rename(columns=lambda x: x.replace('_1', '')),
            tabla1[~tabla1.index.isin(merged.index)]
        ], ignore_index=True)
        tabla2_actualizada = pd.concat([
            no_conflictivos[cols_t2].rename(columns=lambda x: x.replace('_2', '')),
            tabla2[~tabla2.index.isin(merged.index)]
        ], ignore_index=True)
        return tabla1_actualizada, tabla2_actualizada

    def _actualizar_pesos_campos(self, tabla1, tabla2):
        campos_validos = ESTRUCTURA[ESTRUCTURA['tipo'] == 'texto']['campo']
        for campo in campos_validos:
            coincidencias = tabla1[tabla1['match_score'] > self.umbrales['score_inicial']]
            if not coincidencias.empty:
                efectividad = coincidencias[campo].apply(lambda x: x in coincidencias['match_valor']).mean()
                self.pesos_campos[campo] = min(2.0, max(0.5, self.pesos_campos[campo] * (1 + efectividad)))

    def conciliacion_iterativa(self):
        tabla1, tabla2 = self.cargar_datos()
        for self.iteracion in range(self.max_fases):
            self._ajustar_umbrales()
            # Paso 1: Matching exacto
            tabla1, tabla2 = self._match_semilla(tabla1, tabla2)
            # Paso 2: Matching difuso
            tabla1 = self.matching_inteligente(tabla1, tabla2, 'clave_compuesta')
            # Paso 3: Validación y segregación
            tabla1, tabla2 = self._validar_matches(tabla1, tabla2)
            # Paso 4: Actualizar pesos
            self._actualizar_pesos_campos(tabla1, tabla2)
            # Guardar resultados intermedios
            iter_output1 = REPORTS_PATH / f"tabla1_iteracion_{self.iteracion}.csv"
            iter_output2 = REPORTS_PATH / f"tabla2_iteracion_{self.iteracion}.csv"
            tabla1.to_csv(iter_output1, index=False)
            tabla2.to_csv(iter_output2, index=False)
            logging.info(f"Iteración {self.iteracion} guardada en {REPORTS_PATH}")
            if len(tabla1) < self.umbrales['min_matches_por_fase']:
                self.fase += 1
                if self.fase > 3:
                    break
        return tabla1, tabla2

    def generar_reporte(self, tabla1_final, tabla2_final):
        reporte_path = REPORTS_PATH / "Resumen.xlsx"
        with pd.ExcelWriter(reporte_path, engine='xlsxwriter') as writer:
            tabla1_final.to_excel(writer, sheet_name="Tabla1_Final", index=False)
            tabla2_final.to_excel(writer, sheet_name="Tabla2_Final", index=False)
            
            total_t1 = len(tabla1_final)
            total_t2 = len(tabla2_final)
            matches_exactos = tabla1_final['match_score'].eq(100).sum() if 'match_score' in tabla1_final.columns else 0
            matches_fuzzy = tabla1_final[(tabla1_final['match_score'] < 100) & 
                                         (tabla1_final['match_score'] >= self.umbrales['score_inicial'])].shape[0] if 'match_score' in tabla1_final.columns else 0
            matches_total = tabla1_final[tabla1_final['match_valor'].notnull()].shape[0] if 'match_valor' in tabla1_final.columns else 0
            sin_match = tabla1_final[tabla1_final['match_valor'].isnull()].shape[0] if 'match_valor' in tabla1_final.columns else 0
            promedio_score = tabla1_final['match_score'].mean() if total_t1 > 0 and 'match_score' in tabla1_final.columns else 0
            mediana_score = tabla1_final['match_score'].median() if total_t1 > 0 and 'match_score' in tabla1_final.columns else 0

            resumen_data = {
                "Indicador": [
                    "Total Tabla1", "Total Tabla2", "Matches Exactos", "Matches Difusos", "Total Matches",
                    "Sin Match", "Promedio Score", "Mediana Score", "Iteraciones Completadas", "Fase Final",
                    "Umbral Score Final", "Tolerancia Fecha Final", "Tolerancia Importe Final", "Registros Segregados"
                ],
                "Valor": [
                    total_t1, total_t2, matches_exactos, matches_fuzzy, matches_total,
                    sin_match, round(promedio_score, 2), mediana_score, self.iteracion, self.fase,
                    self.umbrales['score_inicial'], self.umbrales['diferencia_fecha'], self.umbrales['tolerancia_importe'],
                    self.contador_segregados
                ]
            }
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
            
            bins = [0, 20, 40, 60, 80, 100]
            df_bins = pd.cut(tabla1_final['match_score'], bins=bins, right=True)
            freq = df_bins.value_counts(sort=False).reset_index()
            freq.columns = ['Rango', 'Frecuencia']
            freq.to_excel(writer, sheet_name="Distribucion_Score", index=False)
            
            workbook  = writer.book
            worksheet = writer.sheets["Distribucion_Score"]
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'name': 'Frecuencia de Match Score',
                'categories': ['Distribucion_Score', 1, 0, len(freq), 0],
                'values': ['Distribucion_Score', 1, 1, len(freq), 1],
            })
            chart.set_title({'name': 'Distribución de Puntaje de Matching'})
            chart.set_x_axis({'name': 'Rango de Puntaje'})
            chart.set_y_axis({'name': 'Frecuencia'})
            worksheet.insert_chart('D2', chart)
            
        logging.info(f"Reporte generado: {reporte_path}")

    def validacion_cruzada(self, tabla_conciliada, porcentaje=0.1):
        muestra = tabla_conciliada.sample(frac=porcentaje)
        muestra_path = REPORTS_PATH / "muestra_validacion_manual.xlsx"
        muestra.to_excel(muestra_path, index=False)
        logging.info(f"Muestra para validación guardada en: {muestra_path}")

if __name__ == "__main__":
    conciliador = ConciliadorAvanzado()
    tabla1_final, tabla2_final = conciliador.conciliacion_iterativa()
    conciliador.generar_reporte(tabla1_final, tabla2_final)
    conciliador.validacion_cruzada(tabla1_final)
