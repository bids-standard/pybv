.PHONY: all inplace test flake pydocstyle check-manifest pep build-doc

all: inplace pep test build-doc

inplace:
	@echo "Installing pybv"
	@python setup.py develop

test:
	@echo "Running pytest"
	@pytest --doctest-modules --cov=./pybv --cov-report=xml --verbose

flake:
	@echo "Running flake8"
	@flake8 --docstring-convention numpy --count pybv

pydocstyle:
	@echo "Running pydocstyle"
	@pydocstyle

check-manifest:
	@echo "Running check-manifest"
	@check-manifest

pep: flake pydocstyle check-manifest

build-doc:
	@echo "Building documentation"
	make -C docs/ clean
	make -C docs/ html
	cd docs/ && make view
