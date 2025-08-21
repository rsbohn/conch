class Response:
    def __init__(self):
        self._json = {"content": [{"text": ""}]}
    def raise_for_status(self):
        pass
    def json(self):
        return self._json

class AsyncClient:
    def __init__(self, *args, **kwargs):
        pass
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def post(self, url, json=None, headers=None):
        return Response()
