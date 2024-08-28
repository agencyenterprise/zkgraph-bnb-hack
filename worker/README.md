# Running the Worker application

## Table of Contents
- [Python Version](#python-version)
- [Installation](#installation)
- [Virtual Environment](#virtual-environment)
- [Installing Packages](#installing-packages)
- [Running the Application](#running-the-application)

## Python Version

This project uses **Python 3.12**. Ensure that you have the correct Python version installed on your system. You can check your Python version by running:

```bash
python --version
```

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/agencyenterprise/zkgraph-bnb-hack.git
    cd zkgraph-bnb-hack/worker
    ```

1. **Install Poetry:**

    Poetry is a dependency management tool for Python. Install it by following the instructions [here](https://python-poetry.org/docs/#installation).

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

    Or use `pip`:

    ```bash
    pip install poetry
    ```

## Virtual Environment

Poetry automatically creates and manages virtual environments. To create a virtual environment, simply run:

```bash
poetry shell
```
This will create and activate the virtual environment. If you want to deactivate it later, just run ```exit```.

## Installing Packages

To install the dependencies specified in your pyproject.toml file, run:

```bash
poetry install
```

## Running the Application

```bash
uvicorn main:app --reload --port=8000
```