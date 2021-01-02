# simple makefile to simplify repetitive build env management tasks under posix

PYTHON ?= python
PYTESTS ?= pytest

all: inplace test

inplace:
	$(PYTHON) setup.py develop

test:
	$(PYTESTS) --doctest-modules --cov=./pybv --cov-report=xml --verbose

flake:
	@if command -v flake8 > /dev/null; then \
		echo "Running flake8"; \
		flake8 --docstring-convention numpy --count pybv; \
	else \
		echo "flake8 not found, please install it!"; \
		exit 1; \
	fi;
	@echo "flake8 passed"

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle

check-manifest:
	@echo "Running check-manifest"
	@check-manifest

pep:
	@$(MAKE) -k flake pydocstyle check-manifest

build-doc:
	cd docs; make clean
	cd docs; make html
	cd docs; make view
