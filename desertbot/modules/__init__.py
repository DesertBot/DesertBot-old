from twisted.plugin import pluginPackagePaths
import os

__path__.extend(pluginPackagePaths(__name__))
for dir, subdirs, files in os.walk(os.path.dirname(os.path.realpath(__file__))):
    for subdir in subdirs:
        __path__.append(os.path.join(dir, subdir)) # Also include all module subdirectories in the path
__all__ = []