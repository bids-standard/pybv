# Contributions

Contributions are welcome in the form of feedback and discussion in issues,
or pull requests for changes to the code.

Once the implementation of a piece of functionality is considered to be free of
bugs and properly documented, it can be incorporated into the `main` branch.

To help developing `pybv`,
you will need a few adjustments to your installation as shown below.

**All contributions are expected to follow the**
[**Code of Conduct of the bids-standard GitHub organization.**](https://github.com/bids-standard/.github/blob/master/CODE_OF_CONDUCT.md)

## Install the development version

First make a fork of the repository under your `USERNAME` GitHub account.
Then, in your Python environment follow these steps:

```Shell
git clone https://github.com/USERNAME/pybv
cd pybv
pip install -r requirements-dev.txt
pip install -e .
```

## Running tests and coverage

If you have followed the steps to get the development version,
you can run tests by making use of the `Makefile` and
[GNU Make](https://www.gnu.org/software/make/).
From the project root, call:

- `make test` to run tests and coverage
- `make pep` to run style checks

## Building the documentation

The documentation can be built using [Sphinx](https://www.sphinx-doc.org).
Again, assuming that you followed the steps to get the development version,
you can use the `Makefile`.
From the project root, call:

- `make build-doc` to build the documentation and open a browser window to view it

The publicly accessible documentation is built and hosted by
[Read the Docs](https://readthedocs.org/).
Credentials for Read the Docs are currently held by:

- [@sappelhoff](https://github.com/sappelhoff/)
- [@choldgraf](https://github.com/choldgraf/)


## Making a release on GitHub, PyPi, and Conda-Forge

`pybv` is regularly released on
[GitHub](https://github.com/bids-standard/pybv/releases),
[PyPI](https://pypi.org/project/pybv/),
and [Conda-Forge](https://anaconda.org/conda-forge/pybv).

Credentials are currently held by:

- GitHub
    - Admin
      - any admin of the [bids-standard GitHub organization](https://github.com/bids-standard)
      - [@sappelhoff](https://github.com/sappelhoff/)
      - [@choldgraf](https://github.com/choldgraf/)
      - [@cbrnr](https://github.com/cbrnr/)
    - Write
      - [@hoechenberger](https://github.com/hoechenberger/)
- PyPi
    - Owner
        - [@sappelhoff](https://github.com/sappelhoff/)
        - [@choldgraf](https://github.com/choldgraf/)
    - Maintainer
        - [@cbrnr](https://github.com/cbrnr/)
- Conda-Forge
    - see: https://github.com/conda-forge/pybv-feedstock#feedstock-maintainers

Releasing on GitHub will automatically trigger a release on PyPi via a GitHub Action
(The credentials for PyPi are stored as "GitHub Secrets").
A release on PyPi in turn will automatically trigger a release on Conda-Forge.
Thus, the release protocol can be briefly described as follows:

1. You will need admin rights for the `pybv` GitHub repository.
1. Go to your Python environment for `pybv`.
1. Make sure all tests pass and the docs are built cleanly.
1. Update the `__version__` variable in `__init__.py`:
    - Remove the `.devN` suffix.
    - If the version preceding the `.devN` suffix is not the version to be
      released, update the version as well according to
      [semantic versioning](https://semver.org/) with its `major.minor.patch`
      style.
1. Copy the version from `__init__.py` to the version metadata field in the
   `CITATION.cff` file.
    - If applicable, append new authors to the author metadata in the `CITATION.cff` file.
1. Update `docs/changelog.rst`, renaming the "current" headline to the new
   version and (if applicable) extending the "Authors" section of the document.
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
   using the git tag from the previous step (e.g., `v1.2.3`).
   Fill the tag name into the "Release title" field, and fill the "Description" field
   as you see fit.
1. This will trigger a GitHub Action that will build the package and release it to PyPi.
1. The PyPi release will trigger a release on Conda-Forge.

Then the release is done and `main` has to be prepared for development of
the next release:

1. Update the `__version__` variable in `__init__.py`:
    - Bump up the `major.minor.patch` version according to
      [semantic versioning](https://semver.org/) so that the version will be
      the version that is planned to be released next (e.g., `1.3.0`).
    - Append `.dev0` to the version (e.g., `1.3.0.dev0`).
1. Note that the version version metadata in the `CITATION.cff` file remains unchanged.
1. Add a "Current (unreleased)" headline to `docs/changelog.rst`.
1. Commit the changes and git push to `main` (or make a pull request).
