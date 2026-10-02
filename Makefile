PYTHON = uv run python
SRC_DIR = src

.PHONY: all install run debug clean lint lint-strict help

all: help

install:
	uv sync

run:
	$(PYTHON) -m $(SRC_DIR)

debug:
	$(PYTHON) -m pdb -m $(SRC_DIR)

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	uv run flake8 . --exclude=data,.venv
	uv run mypy . --exclude '^(data|\.venv)/' --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 . --exclude=data,.venv
	uv run mypy . --strict --exclude '^(data|\.venv)/'

help:
	@echo "Commandes disponibles :"
	@echo "  make install     - Installe les dépendances avec uv"
	@echo "  make run         - Lance le projet"
	@echo "  make debug       - Lance le projet en mode débogage (pdb)"
	@echo "  make clean       - Supprime les caches et fichiers temporaires"
	@echo "  make lint        - Vérifie la qualité du code (flake8 + mypy)"
	@echo "  make lint-strict - Vérifie la qualité du code en mode strict"