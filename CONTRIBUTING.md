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
