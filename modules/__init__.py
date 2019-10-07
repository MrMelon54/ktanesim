from modules.base import Module, noparts, check_solve_cmd, gif_append, gif_output
from os.path import basename, dirname, join as path_join
from glob import glob
import importlib

VANILLA_MODULES = {}
MODDED_MODULES = {}

def _is_module(potential_module):
    # We need a class, not a string or number. (Also, issubclass throws on the latter)
    if not isinstance(potential_module, type):
        return False

    # We need a subclass, not the base Module class itself.
    if potential_module is Module:
        return False

    return issubclass(potential_module, Module)

for module_file in glob(path_join(dirname(__file__), "*.py")):
    if basename(module_file) in {"__init__.py", "base.py"}:
        continue

    module_name = basename(module_file)[:-3]
    imported = importlib.import_module('modules.' + module_name)

    # Find the module class
    try:
        attribute_names = dir(imported)
        attribute_values = (getattr(imported, name) for name in attribute_names)
        module = next(filter(_is_module, attribute_values))
    except StopIteration: # no element matches the filter
        raise Exception(f"Module was not found in the script `{module_name}.py`")

    category = VANILLA_MODULES if module.vanilla else MODDED_MODULES
    category[module_name] = module

async def cmd_modules(channel, author, parts):
    list_ = lambda d: ', '.join(f"`{x}`" for x in d)
    await channel.send(f"Available modules:\nVanilla: {list_(VANILLA_MODULES)}\nModded: {list_(MODDED_MODULES)}")
