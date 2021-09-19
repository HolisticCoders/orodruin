# Orodruin
A Python rigging graph library leveraging a composition based workflow.

# Prerequisites
- [Poetry](https://python-poetry.org/) must be installed
- Python 3.7+ must be installed.
    everything should work with versions higher than 3.7 but that's never been tested.
    If you use pyenv, run `pyenv install 3.7.9` and poetry will pick up on the proper version automatically

# Installation
- Clone the repository.
- cd in `orodruin`.
- Run `poetry config virtualenvs.in-project true --local` to make sure poetry will create the virtualenv inside the project folder.
    Note: Skip the `--local` argument if you want that behavior in every project.
- Run `poetry install --no-dev` to create a new virtual env and install all the dependencies.
    Remove the `--no-dev` argument if you want the dev dependencies.