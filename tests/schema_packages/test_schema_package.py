from nomad.metainfo.metainfo import Package

from plugin_img.schema_packages import schema_package_entry_point


def test_schema_package_entry_point_loads():
    package = schema_package_entry_point.load()
    assert isinstance(package, Package)
    assert 'image_analysis' in package.name
