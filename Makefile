.PHONY: all inplace test flake pydocstyle check-manifest isort black pep build-doc dist-build

all: inplace pep test build-doc dist-build

inplace:
	@echo "Installing pybv"
	@python -m pip install --editable .

test:
	@echo "Running pytest: doctests"
	@pytest pybv/io.py --doctest-modules -W ignore::UserWarning --verbose
	@echo "Running pytest: test modules"
	@pytest --cov=./pybv --cov-report=xml --verbose

flake:
	@echo "Running flake8"
	@flake8 --docstring-convention numpy --count pybv

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle

check-manifest:
	@echo "Running check-manifest"
	@check-manifest

isort:
	@echo "Running check-manifest"
	@isort .

black:
	@echo "Running black"
	@black .

pep: flake pydocstyle check-manifest isort black

build-doc:
	@echo "Building documentation"
	make -C docs/ clean
	make -C docs/ html
	cd docs/ && make view

dist-build:
	@echo "Building dist"
	rm -rf dist
	@python -m build
