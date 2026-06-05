# References

## Parser

The main parser class is `plugin_img.parsers.root_parser.DataRootParser`.

It exports the following behavior:

- `parse(mainfile, archive, logger)` — parse a sample folder and write `archive.data`
- `_find_synthesis_json(data_root)` — locate sample-level JSON metadata
- `_parse_image_folder(image_folder, data_root, log)` — parse one image experiment folder
- `_convert_npy_to_png(npy_path, log)` — generate a preview image from a raw NPY array

## Schema package

The plugin registers one schema package entry point:

- `plugin_img.schema_packages:schema_package_entry_point`

The schema package is defined in `plugin_img.schema_packages.image_analysis.m_package` and contains image analysis sections for:

- `ImageDataset`
- `ImageExperimentRun`
- `ImageMetadata`
- `ImageData`
- `ImageDimensions`
- `RegionOfInterest`
- `BoundingBox`
- `ImageVisualization`

## Sample data layout

Supported files and folders include:

- `synthesis.json` — sample-level synthesis or experiment conditions
- `metadata.json` — per-experiment image metadata
- `image_raw.npy` — raw image array data
- `image_preview.png` — preview image for visualization
- `manifest.csv` — legacy experiment manifest data
