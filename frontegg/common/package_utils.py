from importlib import import_module


class PackageUtils:
    @staticmethod
    def load_package(name: str):
        try:
            return import_module(name)
        except ImportError as e:
            raise Exception(name + ' is not installed')
