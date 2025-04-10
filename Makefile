.PHONY: clean clean-data lint test docs help install

.DEFAULT_GOAL := help

#################################################################################
# VARIABLES                                                                       #
#################################################################################

PROJECT_DIR := $(CURDIR)
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                        #
#################################################################################

install: ## Install development dependencies
	$(PYTHON_INTERPRETER) -m pip install -r requirements_dev.txt

clean: ## Remove Python file artifacts and cached files
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf build/
	rm -rf dist/

clean-data: ## Remove generated data files
	rm -rf data/processed/*
	rm -rf reports/*

lint: ## Check style with ruff
	ruff check .
	ruff format .

test: ## Run tests with pytest
	pytest tests/ -v --cov=src

docs: ## Generate Sphinx HTML documentation
	rm -f docs/match_sync_lite.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ src/match_sync_lite
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

generate-data: ## Generate sample data for testing
	$(PYTHON_INTERPRETER) scripts/generate_data.py

run: ## Run the reconciliation pipeline
	$(PYTHON_INTERPRETER) main.py

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make [target]'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z_-]+:.*?## .*$$/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
