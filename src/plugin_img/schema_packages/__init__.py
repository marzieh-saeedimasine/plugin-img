"""Schema package compatibility shim for `plugin_img`.

`pyproject.toml` declares the schema package entry-point as
`plugin_img.schema_packages:schema_package_entry_point`. The actual
implementation lives in the top-level `images` package; re-export the
expected symbol here so entry-point resolution succeeds.
"""

try:
    from plugin_img.images import schema_package_entry_point  # type: ignore
except Exception:
    try:
        from plugin_img.hyperspectral import schema_package_entry_point  # type: ignore
    except Exception:
        schema_package_entry_point = None  # type: ignore

__all__ = ['schema_package_entry_point']
