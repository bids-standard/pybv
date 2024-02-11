.PHONY: all inplace test check-manifest build-doc dist-build

all: inplace check-manifest test build-doc dist-build

inplace:
	@echo "Installing pybv"
	@python -m pip install --editable .

test:
	@echo "Running pytest: doctests"
	@pytest pybv/io.py --doctest-modules -W ignore::UserWarning --verbose
	@echo "Running pytest: test modules"
	@pytest --cov=./pybv --cov-report=xml --verbose

check-manifest:
	@echo "Running check-manifest"
	@check-manifest

build-doc:
	@echo "Building documentation"
	make -C docs/ clean
	make -C docs/ html
	cd docs/ && make view

dist-build:
	@echo "Building dist"
	rm -rf dist
	@python -m build
