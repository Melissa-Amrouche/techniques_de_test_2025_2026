.PHONY: test unit_test perf_test coverage lint doc doc_pdf clean

# Variables
PYTHON = ../.venv/bin/python
PYTEST = ../.venv/bin/pytest
COVERAGE = ../.venv/bin/coverage
RUFF = ../.venv/bin/ruff
PDOC = ../.venv/bin/pdoc3
export PYTHONPATH := $(shell pwd)/..

# Lance tous les tests (unitaires + performance)
test:
	$(PYTEST) tests/ -v

# Lance uniquement les tests unitaires (sans les tests de performance)
unit_test:
	$(PYTEST) tests/ -v -m "not performance"

# Lance uniquement les tests de performance
perf_test:
	$(PYTEST) tests/ -v -m "performance"

# Génère un rapport de couverture de code
coverage:
	$(COVERAGE) run -m pytest tests/
	$(COVERAGE) report
	$(COVERAGE) html

# Valide la qualité de code avec ruff
lint:
	$(RUFF) check triangulator/ --exclude visualizer.py

# Génère la documentation HTML
doc:
	$(PDOC) --html --output-dir docs triangulator/ --force

# Génère la documentation PDF
doc_pdf:
	$(PYTHON) generate_pdf_simple.py

# Nettoie les fichiers générés
clean:
	rm -rf htmlcov/
	rm -rf docs/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
