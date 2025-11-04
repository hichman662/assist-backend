# app/services/dotnet_client.py
import os
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class DotNetClient:
    def __init__(self):
        base_url = os.getenv("MOSIOT_BASE_URL", "").rstrip("/")
        if not base_url:
            raise ValueError("MOSIOT_BASE_URL is required (e.g. https://localhost:44358/api)")
        self.base_url = base_url

        # Optional fallback token (only used if no user Authorization header is provided)
        self.service_token = os.getenv("MOSIOT_SERVICE_TOKEN")

        # TLS verification (set MOSIOT_VERIFY_TLS=false to disable for local/self-signed)
        verify_env = os.getenv("MOSIOT_VERIFY_TLS", "true").strip().lower()
        self.verify_tls = not (verify_env in ("0", "false", "no"))

        # Reusable Session with retry policy
        self.session = requests.Session()
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.25,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _headers(self, auth_header: Optional[str]) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header
        elif self.service_token:
            headers["Authorization"] = self.service_token
        return headers

    def _url(self, path: str) -> str:
        # path should start with "/", e.g., "/IMCareActivity/ReadByTime"
        return f"{self.base_url}{path}"

    def get(
        self,
        path: str,
        auth_header: Optional[str],
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        resp = self.session.get(
            self._url(path),
            headers=self._headers(auth_header),
            params=params,
            timeout=timeout,
            verify=self.verify_tls,
        )
        return self._normalize(resp)

    def post(
        self,
        path: str,
        auth_header: Optional[str],
        json: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        resp = self.session.post(
            self._url(path),
            headers={**self._headers(auth_header), "Content-Type": "application/json"},
            json=json or {},
            timeout=timeout,
            verify=self.verify_tls,
        )
        return self._normalize(resp)

    @staticmethod
    def _normalize(resp: requests.Response) -> Dict[str, Any]:
        try:
            data = resp.json()
        except ValueError:
            data = {"_text": resp.text}
        return {
            "ok": resp.ok,
            "status": resp.status_code,
            "reason": resp.reason,
            "data": data,
        }


dotnet_client = DotNetClient()
