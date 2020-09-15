class HttpException(Exception):
    def __init__(self, content, status_code: int, headers={}):
        self.status_code = status_code
        self.content = content
        self.headers = headers


class UnauthenticatedException(HttpException):
    def __init__(self, content='Unauthenticated', status_code: int = 401, headers={}):
        super(UnauthenticatedException, self).__init__(content, status_code)


class UnauthorizedException(HttpException):
    def __init__(self, content='Unauthorized', status_code: int = 403, headers={}):
        super(UnauthorizedException, self).__init__(content, status_code)
