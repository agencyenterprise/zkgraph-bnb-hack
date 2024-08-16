import datetime
import typing

import requests
from pycognito.utils import RequestsSrpAuth

BASE_RELAY_API = "https://defender-api.openzeppelin.com/relayer/"
BASE_RELAYER_API = "https://api.defender.openzeppelin.com/"

class RelayException(Exception):
    """Base exception for Relay API errors"""

    pass


class RelayTimeoutError(RelayException):
    """Timeout exception"""

    pass


class RelayUnauthorizedError(RelayException):
    """Unauthorized exception"""

    pass

class BaseClient:
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        aws_user_pool_id: str,
        aws_client_id: str,
        aws_srp_pool_region: str,
        base_api: str,
        **kwargs,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.aws_user_pool_id = aws_user_pool_id
        self.aws_client_id = aws_client_id
        self.aws_srp_pool_region = aws_srp_pool_region
        self.base_api = base_api

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
        }

    @property
    def auth(self) -> RequestsSrpAuth:
        return RequestsSrpAuth(
            username=self.api_key,
            password=self.api_secret,
            user_pool_id=self.aws_user_pool_id,
            client_id=self.aws_client_id,
            user_pool_region=self.aws_srp_pool_region,
        )

    def get(self, path: str, params: dict = None) -> requests.Response:
        try:
            response = requests.get(
                self.base_api + path,
                params=params,
                headers=self.headers,
                auth=self.auth,
                timeout=60,
            )
        except requests.ReadTimeout:
            raise RelayTimeoutError(f"GET: {self.base_api + path}")

        return response

    def post(self, path: str, payload: dict = None) -> requests.Response:
        try:
            response = requests.post(
                self.base_api + path,
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=60,
            )
        except requests.ReadTimeout:
            raise RelayTimeoutError(f"POST: {self.base_api + path}")

        return response

    def put(self, path: str, payload: dict = None) -> requests.Response:
        try:
            response = requests.put(
                self.base_api + path,
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=60,
            )
        except requests.ReadTimeout:
            raise RelayTimeoutError(f"PUT: {self.base_api + path}")

        return response

    def delete(self, path: str) -> requests.Response:
        try:
            response = requests.delete(
                self.base_api + path,
                headers=self.headers,
                auth=self.auth,
                timeout=60,
            )
        except requests.ReadTimeout:
            raise RelayTimeoutError(f"DELETE: {self.base_api + path}")

        return response

    def _handle_response(self, response: requests.Response) -> dict:
        if not response.ok:
            raise self._relayer_exception(response)

        return response.json()

    def _relayer_exception(self, response: requests.Response) -> RelayException:
        # TODO: @ssavarirayan add status code parsing and raise specific exceptions
        try:
            message = response.json()["message"]
            return RelayException(message)
        except:
            # if error parsing fails, return the entire response
            return RelayException(response.json())

class RelayClient(BaseClient):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        aws_user_pool_id: str = "us-west-2_94f3puJWv",
        aws_client_id: str = "40e58hbc7pktmnp9i26hh5nsav",
        aws_srp_pool_region: str = "us-west-2",
    ):
        super().__init__(
            api_key,
            api_secret,
            aws_user_pool_id,
            aws_client_id,
            aws_srp_pool_region,
            BASE_RELAY_API,
        )

    def get_relayer(self, relayer_id: str) -> requests.Response:
        response = self.get(f"relayers/{relayer_id}")

        return self._handle_response(response)

    def list_relayers(self) -> requests.Response:
        response = self.get("relayers/summary")

        return self._handle_response(response)

    def list_relayer_keys(self, relayer_id: str) -> requests.Response:
        response = self.get(f"relayers/{relayer_id}/keys")

        return self._handle_response(response)

    def create_relayer(self, data: dict) -> requests.Response:
        response = self.post("relayers", data)

        return self._handle_response(response)

    def create_relayer_key(self, relayer_id: str) -> requests.Response:
        response = self.post(f"relayers/{relayer_id}/keys")

        return self._handle_response(response)

    def update_relayer(self, relayer_id: str, data: dict) -> requests.Response:
        initial_data = self.get_relayer(relayer_id)

        if "policies" in data:
            response = self.update_relayer_policies(relayer_id, data["policies"])

            if len(data) == 1:
                return self._handle_response(response)

        payload = initial_data | data
        response = self.put(f"relayers", payload)

        return self._handle_response(response)

    def update_relayer_policies(self, relayer_id: str, data: dict) -> requests.Response:
        initial_data = self.get_relayer(relayer_id)["policies"]
        payload = initial_data | data
        response = self.put(f"relayers/{relayer_id}", payload)

        return self._handle_response(response)

    def delete_relayer_key(self, relayer_id: str, key_id: str) -> requests.Response:
        response = self.delete(f"relayers/{relayer_id}/keys/{key_id}")

        return self._handle_response(response)

class RelayerClient(BaseClient):
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        aws_user_pool_id: str = "us-west-2_iLmIggsiy",
        aws_client_id: str = "1bpd19lcr33qvg5cr3oi79rdap",
        aws_srp_pool_region: str = "us-west-2",
        json_rpc_request_id: int = 0,
    ):
        super().__init__(
            api_key,
            api_secret,
            aws_user_pool_id,
            aws_client_id,
            aws_srp_pool_region,
            BASE_RELAYER_API,
        )
        self.json_rpc_request_id = json_rpc_request_id

    def get_relayer(self) -> requests.Response:
        response = self.get("relayer")

        return self._handle_response(response)

    def send_transaction(self, data: dict) -> requests.Response:
        response = self.post("txs", data)

        return self._handle_response(response)

    def get_transaction(self, tx_id: str) -> requests.Response:
        response = self.get(f"txs/{tx_id}")

        return self._handle_response(response)

    def replace_transaction_by_id(self, tx_id: str, data: dict) -> requests.Response:
        response = self.put(f"txs/{tx_id}", data)

        return self._handle_response(response)

    def replace_transaction_by_nonce(self, nonce: int, data: dict) -> requests.Response:
        response = self.put(f"txs/{nonce}", data)

        return self._handle_response(response)

    def list_transactions(
        self, status: str = None, limit: int = None, since: datetime.datetime = None
    ) -> requests.Response:
        params = {}

        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        if since:
            params["since"] = since

        response = self.get("txs", params)

        return self._handle_response(response)

    def sign(self, data: dict) -> requests.Response:
        response = self.post("sign", data)

        return self._handle_response(response)

    def sign_typed_data(self, data: dict) -> requests.Response:
        response = self.post("sign-typed-data", data)

        return self._handle_response(response)

    def call_json_rpc(self, method: str, params: typing.List[str]) -> requests.Response:
        self.json_rpc_request_id += 1

        data = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": self.json_rpc_request_id,
        }

        response = self.post("relayer/jsonrpc", data)

        return self._handle_response(response)