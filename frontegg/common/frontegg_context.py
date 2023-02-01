from frontegg.common.package_utils import PackageUtils


class FronteggContext(object):
    _instance = None
    options = {}

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(FronteggContext, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    @staticmethod
    def init(options={}):
        FronteggContext().__validate_options(options)
        FronteggContext().options = options

    def __validate_options(self, options):
        if options.get('access_tokens_options', None) is not None:
            self.__validate_access_tokens_options(options.get('access_tokens_options'))

    def __validate_access_tokens_options(self, access_tokens_options):
        if access_tokens_options.get('cache') is None:
            raise Exception("'cache' is missing from access tokens options")

        if access_tokens_options.get('cache').get('type') == 'redis':
            self.__validate_redis_options(access_tokens_options.get('cache').get('options', {}))

    def __validate_redis_options(self, redis_options):
        PackageUtils.load_package('redis')

        required_properties = ['host', 'password', 'port', 'db']
        for required_property in required_properties:
            if redis_options.get(required_property, None) is None:
                raise Exception(required_property + ' is missing from redis cache options')
