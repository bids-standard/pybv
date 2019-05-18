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

##### Making a release
(needs admin rights for GitHub and PyPi)

1. go to your python environment for `pybv`
1. run `pip install -U setuptools wheel twine`
1. update the `__version__` variable in `__init__.py`
    - remove the `.devN` suffix
    - if the version preceding the `.devN` suffix is not the version to be
      released, update the version as well according to
      [semantic versioning](https://semver.org/) with its `major.minor.patch`
      style.
1. commit the change and git push to master (or make a pull request)
1. run `pip install -e .` and then `python setup.py sdist bdist_wheel`
1. run `twine upload dist/*` to upload to pypi
1. Make a [release on GitHub](https://help.github.com/en/articles/creating-releases)
   , simultaneously making a git tag that is named like the current version
   with a prefix of `v` (e.g., `1.2.3` --> `v1.2.3`)

Then the release is done and `master` has to be prepared for development of
the next release:

1. update the `__version__` variable in `__init__.py`
    - bump up the `major.minor.patch` version according to
      [semantic versioning](https://semver.org/) so that the version will be
      the version that is planned to be released next (e.g., `1.3.0`)
    - append `.dev0` to the version (e.g., `1.3.0.dev0`)
    - commit the change and git push to master (or make a pull request)
