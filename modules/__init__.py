from modules.base import Module, noparts, check_solve_cmd, gif_append, gif_output
import glob
from os.path import join as pjoin
from os.path import dirname as pdir
from os.path import basename as pbase
import importlib

VANILLA_MODULES={}
MODDED_MODULES={}

for moduleScript in glob.glob(pjoin(pdir(__file__),"*.py")):
    if pbase(moduleScript) in ["__init__.py","base.py"]:
        continue
    moduleName=pbase(moduleScript)[:-3]
    moduleImport=importlib.import_module('modules.'+moduleName)
    attributeList=dir(moduleImport)
    for attrName in attributeList:
        testAttr=getattr(moduleImport,attrName)
        if isinstance(testAttr,Module):
            if testAttr.vanilla:
                VANILLA_MODULES[moduleName]=testAttr
            else:
                MODDED_MODULES[moduleName]=testAttr
            break
    else:
        raise Exception(f"Module was not found in the script `{moduleName}.py`")

async def cmd_modules(channel, author, parts):
    list_ = lambda d: ', '.join(f"`{x}`" for x in d)
    await channel.send(f"Available modules:\nVanilla: {list_(VANILLA_MODULES)}\nModded: {list_(MODDED_MODULES)}")
