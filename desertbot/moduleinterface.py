from zope.interface import Attribute, Interface


class IModule(object):
    name = Attribute("The module name.")
