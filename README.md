# MatchSync Lite

**MatchSync Lite** es una solución ligera para la conciliación de datos en la industria retail, diseñada para automatizar la comparación entre las ventas diarias registradas en el sistema de caja y los depósitos bancarios recibidos.  
El objetivo principal es reducir el trabajo manual, minimizar errores y acelerar el proceso de conciliación en entornos de pequeña escala, como una tienda de ropa independiente con varias sucursales.

## 🚀 ¿Qué hace Match Sync Lite?

- 🔍 Compara dos archivos de datos (por ejemplo, dos Excel con inventario)
- 🧠 Genera claves compuestas a partir de campos relevantes
- 📊 Encuentra coincidencias exactas e inexactas
- 🔁 Aplica una lógica iterativa de conciliación
- 📁 Genera reportes y archivos separados con los datos conciliados y no conciliados
- 💻 Genera un archivo de configuración con los parámetros de conciliación
- 📦 Genera un archivo de resultados con los datos 

## Características

- **Generación de Datos de Ejemplo:**  
  Utiliza **Faker** para generar datos simulados de ventas y depósitos bancarios.

- **Configuración Dinámica:**  
  La configuración de los campos se define en un archivo `estructura.xlsx`, lo que permite ajustar fácilmente los parámetros de conciliación.

- **Matching Difuso:**  
  Emplea **RapidFuzz** para realizar comparaciones de texto y encontrar coincidencias basadas en el campo clave ("referencia").

- **Conciliación Iterativa:**  
  El proceso se ejecuta en varias iteraciones, ajustando dinámicamente umbrales y pesos para mejorar la precisión del matching.

- **Generación de Reportes y Visualizaciones:**  
  Se generan reportes en Excel con indicadores clave y gráficos que muestran la distribución del puntaje de matching.

## Estructura del Proyecto

La estructura del proyecto sigue el estándar de [cookiecutter-data-science](https://github.com/drivendata/cookiecutter-data-science), organizada de la siguiente forma:

my_matchsync_project/ 
├── data/ 
│ ├── raw/ # Datos originales: estructura.xlsx, tabla1.xlsx, tabla2.xlsx 
│ └── processed/ # (Opcional) Datos procesados 
├── notebooks/ # Notebooks para exploración y validación 
├── reports/ # Reportes y visualizaciones generados 
├── scripts/ # Scripts auxiliares: 
│ ├── genera_estructura.py # Genera el archivo de estructura de configuración 
│ └── generate_data.py # Genera datos de ventas y depósitos con Faker 
├── src/ 
│ ├── data/ 
│ │    └── process_data.py # Módulo de procesamiento y conciliación 
│ └── visualization/ 
│      └── plot_results.py # (Opcional) Módulo para generar visualizaciones adicionales 
├── tests/ # Pruebas unitarias 
├── main.py # Script de entrada para ejecutar todo el pipeline 
├── README.md # Documentación del proyecto 
└── environment.yml # Definición del entorno de trabajo

## Instalación

1. Clona el repositorio:

   git clone https://github.com/tu_usuario/matchsync-lite.git
   cd matchsync-lite

2. Crea y activa el entorno virtual (por ejemplo, con venv):

    python -m venv MatchSync_Lite_env

    MatchSync_Lite_env\Scripts\activate

3. Instala las dependencias:

    pip install -r requirements.txt


## Uso

Desde la raíz del proyecto, ejecuta el siguiente comando para generar la estructura, los datos de ejemplo y ejecutar el proceso de conciliación:


    python main.py

Este comando realizará lo siguiente:

- Generar el archivo estructura.xlsx en data/raw/.

- Generar los datos de ventas (tabla1.xlsx) y depósitos (tabla2.xlsx) en data/raw/ usando Faker.

- Ejecutar el proceso de conciliación, generando reportes en la carpeta reports/.

- (Opcional) Generar una visualización adicional con la distribución del puntaje de matching.

## Contribuciones
Si deseas contribuir al proyecto, por favor haz un fork del repositorio, realiza tus cambios y envía un pull request.

## Licencia
Este proyecto está licenciado bajo la MIT License.

## Contacto

🧑‍💻 Autor
Ingeniero Ariel Luján Giamportone
📧 [giamportone1@gmail.com]
🔗 (LinkedIn): [https://www.linkedin.com/in/agiamportone/] | (GitHub): [https://github.com/arielgiamportone]

Para cualquier consulta o sugerencia, puedes contactar a mi correo electrónico.