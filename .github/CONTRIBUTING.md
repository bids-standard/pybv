Contributions
-------------

Contributions are welcome in the form of feedback and discussion in issues, or
pull requests for changes to the code.

Once the implementation of a piece of functionality is considered to be free of
bugs and properly documented, it can be incorporated into the `main` branch.

To help developing `pybv`, you will need a few adjustments to your
installation as shown below.

##### Install the development version

First make a fork of the repository under your `USERNAME` GitHub account. Then,
in your Python environment follow these steps:

    $ git clone https://github.com/USERNAME/pybv
    $ cd pybv
    $ pip install -r requirements-dev.txt
    $ pip install -e .

##### Running tests and coverage

If you have followed the steps to get the development version, you can run
tests by simply calling `pytest` from the project root.

##### Building the documentation

The documentation can be built using sphinx. Again, assuming that you followed
the steps to get the development version, you can from the command line
navigate to the `/docs` directory and call `make html`. The HTML pages will
be in `_build/html`.

##### Making a release

You will need admin rights for GitHub.
The PyPi credentials are handled via a "GitHub secret"

1. go to your python environment for `pybv`
1. Make sure all tests pass and the docs are built cleanly
1. update the `__version__` variable in `__init__.py`
    - remove the `.devN` suffix
    - if the version preceding the `.devN` suffix is not the version to be
      released, update the version as well according to
      [semantic versioning](https://semver.org/) with its `major.minor.patch`
      style.
1. Update `docs/changelog.rst`, renaming the "current" headline to the new
   version and (if applicable) extending the "Authors" section of the document
    - "Authors" are all people who committed code or in other ways contributed
    to `pybv` (e.g., by extensively reviewing PRs).
1. Commit the change and git push to `main` (or make a pull request and merge it).
   Include "REL" in your commit message.
1. Then, make an annotated tag `git tag -a -m "v1.2.3" v1.2.3 upstream/main` (This
   assumes that you have a git remote configured with the name "upstream" and
   pointing to https://github.com/bids-standard/pybv). Note also that the
   version from `__init__.py` is preprended with a `v`: `1.2.3` --> `v1.2.3`
   **NOTE: Make sure you have your `main` branch up to date for this step!**
1. `git push --follow-tags upstream`
1. Make a [release on GitHub](https://help.github.com/en/articles/creating-releases),
   using the git tag from the previous step (e.g., `v1.2.3`). Fill the tag name
   into all fields of the release.
1. This will trigger a GitHub Action that will build the package and release it to PyPi.

Then the release is done and `main` has to be prepared for development of
the next release:

1. update the `__version__` variable in `__init__.py`
    - bump up the `major.minor.patch` version according to
      [semantic versioning](https://semver.org/) so that the version will be
      the version that is planned to be released next (e.g., `1.3.0`)
    - append `.dev0` to the version (e.g., `1.3.0.dev0`)
1. add a "Current (unreleased)" headline to `docs/changelog.rst`
1. commit the changes and git push to `main` (or make a pull request)
