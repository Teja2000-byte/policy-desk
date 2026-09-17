import httpx


class APIError(Exception):
    def __init__(self, message: str, status: int = 0):
        super().__init__(message)
        self.status = status


def request_api(
    method: str, path: str, *, base_url: str, token: str | None = None, payload=None, params=None
):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = httpx.request(
            method,
            base_url.rstrip("/") + path,
            headers=headers,
            json=payload,
            params=params,
            timeout=httpx.Timeout(270, connect=5),
        )
    except httpx.HTTPError:
        raise APIError("Cannot reach the decision service. Start the backend and try again.") from None
    if response.is_error:
        try:
            detail = response.json().get("detail", "The request could not be completed.")
            if isinstance(detail, list):
                detail = "; ".join(f"{item['loc'][-1]}: {item['msg']}" for item in detail)
        except (ValueError, AttributeError, KeyError):
            detail = "The service returned an unexpected error. Please try again."
        raise APIError(str(detail), response.status_code)
    return response.json()
