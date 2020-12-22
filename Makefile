# simple makefile to simplify repetitive build env management tasks under posix

# caution: testing won't work on windows, see README

PYTHON ?= python
PYTESTS ?= pytest

all: inplace test

inplace:
	$(PYTHON) setup.py develop

test-doc:
	$(PYTESTS) --doctest-modules --doctest-ignore-import-errors pybv

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

pep:
	@$(MAKE) -k flake pydocstyle

build-doc:
	cd doc; make clean
	cd doc; make html
