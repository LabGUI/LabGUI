__all__ = ['UserTool','test']

from importlib import import_module
import os
import sys
import pkgutil

for (_, name, _) in pkgutil.iter_modules([os.path.dirname(os.path.dirname(__file__))]):
    if name == 'LabTools':
        imported_module = import_module('.', package=name)
        print(dir(imported_module))
        if hasattr(imported_module, 'UserScriptModule'):
            user = imported_module.UserScriptModule.UserScript

UserScript = user