.PHONY: all inplace test flake pydocstyle check-manifest pep build-doc

all: inplace test

inplace:
	python setup.py develop

test:
	pytest --doctest-modules --cov=./pybv --cov-report=xml --verbose

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

pep: flake pydocstyle check-manifest

build-doc:
	make -C docs/ clean
	make -C docs/ html
	make -C docs/ view
