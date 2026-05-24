# mlproject

![PyPI version](https://img.shields.io/pypi/v/mlproject.svg)

this is the basic end to end ml project tutorial

* Created by **[Medhari rakesh](0.0.1)**
  * GitHub: https://github.com/Rakeshavs
  * PyPI: https://pypi.org/user/Rakeshavs/
* PyPI package: https://pypi.org/project/mlproject/
* Free software: MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://Rakeshavs.github.io/mlproject/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/mlproject.git
cd mlproject

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `mlproject`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

mlproject was created in 2026 by Medhari rakesh.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
