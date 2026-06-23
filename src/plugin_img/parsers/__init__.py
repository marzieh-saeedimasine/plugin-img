"""Parser container package for `plugin_img`.

This package will import available parser subpackages (e.g. `old_codes`)
and modules on import so that discovery/registration side-effects occur.
"""

import pkgutil
from importlib import import_module

__all__ = []

for _finder, name, ispkg in pkgutil.iter_modules(__path__):
    try:
        import_module(f'{__name__}.{name}')
        __all__.append(name)
    except Exception:
        pass

# For compatibility with the entry-point declared in pyproject.toml
# (which points to `plugin_img.parsers:parser_entry_point`) attempt
# to re-export any `parser_entry_point` defined in sibling top-level
# packages (for example `hyperspectral`). This keeps the plugin
# declarative entry-point stable while allowing the implementation to
# live in a dedicated top-level module.
#try:
    # Prefer the composite entry point that handles a single synthesis
    # file and delegates to both image and hyperspectral parsers.
#    from plugin_img.parsers.composite import parser_entry_point  # type: ignore
#except Exception:
try:
    from plugin_img.hyperspectral import parser_entry_point  # type: ignore
except Exception:
    try:
        from plugin_img.images import parser_entry_point  # type: ignore
    except Exception:
        parser_entry_point = None  # type: ignore
        
if 'parser_entry_point' not in __all__:
    __all__.append('parser_entry_point')
