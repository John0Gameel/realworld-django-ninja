import requests
from pydantic import BaseModel, SecretStr


class MyAPI:
    base_url = None
    auth_type = None
    auth_token = None

    def __init__(self, base_url, auth_type=None, auth_token=None):
        self.base_url = base_url
        self.auth_type = auth_type
        self.auth_token = auth_token

    def api_request(api_req_fun):
        def inner_api_request(self, *args, **kwargs):
            endpoint = kwargs.pop("endpoint", args[0])
            url = f"{self.base_url}{endpoint}"
            auth_token = kwargs.pop("auth_token", None)
            self._update_kwargs_with_auth(kwargs, auth_token)
            if kwargs.get("json", {}):
                kwargs["json"] = self._prepare_payload(kwargs["json"])
            if kwargs.get("data", {}):
                kwargs["data"] = self._prepare_payload(kwargs["data"])
            return api_req_fun(self, url, **kwargs)

        return inner_api_request

    def _update_kwargs_with_auth(self, kwargs, auth_token=None):
        if auth_token:
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"]["Authorization"] = f"{self.auth_type} {auth_token or self.auth_token}"

    def _prepare_payload(self, payload):
        if isinstance(payload, BaseModel):
            return self._prepare_payload(payload.model_dump())
        if isinstance(payload, SecretStr):
            return payload.get_secret_value()
        if type(payload) is dict:
            prepared_payload = {}
            for k, v in payload.items():
                if isinstance(v, (SecretStr | BaseModel | dict)):
                    prepared_payload[k] = self._prepare_payload(v)
                else:
                    prepared_payload[k] = v
            return prepared_payload
        else:
            return payload

    @api_request
    def get(self, url, **kwargs):
        response = requests.get(url, **kwargs)
        return response

    @api_request
    def post(self, url, **kwargs):
        response = requests.post(url, **kwargs)
        return response

    @api_request
    def put(self, url, **kwargs):
        response = requests.put(url, **kwargs)
        return response

    @api_request
    def delete(self, url, **kwargs):
        response = requests.delete(url, **kwargs)
        return response

    @api_request
    def patch(self, url, **kwargs):
        response = requests.patch(url, **kwargs)
        return response
