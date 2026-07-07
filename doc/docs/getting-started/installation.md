# Installation

## Prerequisites

- Python 3.10 or later

!!! tip pip not found
    If `pip` is not found, try `pip3` or `python3 -m pip` instead.
    Inside an active virtual environment `pip` always works.

## Install via pipx (recommended)

```shell
pipx install py-crap
```

## Install via pip

Requires an active virtual environment (PEP 668):

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install py-crap
```

## Install from source

```shell
git clone https://github.com/padiazg/py-crap.git
cd py-crap
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Verify Installation

```shell
py-crap --help
```

This prints the command help text, confirming the binary is working.
