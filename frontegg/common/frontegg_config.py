class FronteggConfig:
    client_id: str = None
    api_key: str = None

    def __init__(self, client_id: str, api_key):
        if client_id is None:
            raise Exception('client_id is required')
        if api_key is None:
            raise Exception('api_key is required')

        self.client_id = client_id
        self.api_key = api_key
