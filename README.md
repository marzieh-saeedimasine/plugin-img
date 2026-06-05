# plugin-img

`plugin-img` is a NOMAD parser plugin for image analysis datasets. It parses sample folders that contain image metadata, raw image arrays, and optional preview files and converts them into NOMAD entry data.

### Features

- Parses image folders with `metadata.json`, `image_raw.npy`, `image_preview.png`, and `manifest.csv`
- Derives image dimensions, color settings, ROI, and preview visualization
- Supports sample-level synthesis conditions via JSON files
- Creates a NOMAD entry even when no image files are available, using the sample metadata fallback

## Supported data layout

The parser is designed for a sample folder structure like:

```text
sample-folder/
  nomad_collect.txt
  synthesis.json
  <timestamp-folder>/
    metadata.json
    image_raw.npy
    image_preview.png
    manifest.csv
```

The parser also accepts other folder names and formats if they contain one of the supported image metadata or image file types.

## Installation

From the repository root:

```powershell
Set-Location .\packages\plugin-img
uv pip install -e '.[dev]'
```

Python 3.10, 3.11, or 3.12 are supported.

## Run the tests

Run the plugin tests from the package root:

```powershell
python -m pytest -sv tests
```

If you want coverage:

```powershell
uv pip install pytest-cov
python -m pytest --cov=src tests
```

## Development workflow

Lint and format with Ruff:

```powershell
ruff check .
ruff format . --check
```

## Local documentation

Build and serve the plugin documentation locally:

```powershell
mkdocs serve
```

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Run the parser tests and verify documentation changes.
4. Open a pull request with a clear description and test results.

## Contact

- Plugin author: marzieh.saeedimasine@gmail.com
