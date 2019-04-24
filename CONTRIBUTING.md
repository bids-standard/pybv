Contributions
-------------

 Contributions are welcome in the form of feedback and discussion in issues,
 or pull requests for changes to the code.

Once the implementation of a piece of functionality is considered to be free of
bugs and properly documented, it can be incorporated into the master branch.

To help developing `pybv`, you will need a few adjustments to your
installation as shown below.

##### Install the development version

First make a fork of the repository under your USERNAME Github account. Then
follow these steps:

    $ pip uninstall pybv
    $ git clone https://github.com/USERNAME/pybv
    $ cd pybv
    $ pip install -e .

##### Running tests and coverage

To run the tests using `pytest`, you need to install the following:

    $ pip install pytest pytest-cov coverage

Then you can run tests by simply calling `pytest` from the project root.

For coverage, from the root call:

    $ coverage run --source pybv -m pytest

and then `coverage report` to see the report, or alternatively `coverage html`,
which will save an HTML report in `htmlcov/` that you can view in your browser.

##### Building the documentation

The documentation can be built using sphinx. For that, please additionally
install the following:

    $ pip install sphinx alabaster

Then from the command line navigate to the `/docs` directory and call `make
html`. The HTML pages will be in `_build/html`.

##### Making a release (needs admin rights)
1. go to your python environment for `pybv`
1. run `pip install -U setuptools wheel twine`
1. update the `__version__` variable in `__init__.py`
1. commit the change and then git tag the commit with the version
1. git push to master (or make a pull request)
1. also push the git tag to upstream: `git push upstream --tags`
1. run `python setup.py sdist bdist_wheel`
1. run `twine upload dist/*` (needs admin rights for pypi)
1. Make a release on GitHub
1. append `-dev` to the `__version__` variable in `__init__.py` (updating it
   accordingly)
