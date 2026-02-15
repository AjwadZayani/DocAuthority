import requests

SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def handle_api_request(url, method="GET", data=None, headers=None, timeout=10):
    """
    Handles API requests and returns a structured result.
    """
    verb = method.upper()
    if verb not in SUPPORTED_METHODS:
        return {
            "ok": False,
            "status": None,
            "data": None,
            "error": f"Unsupported method: {method}",
        }

    try:
        response = requests.request(
            verb,
            url,
            json=data,
            headers=headers,
            timeout=timeout,
        )

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            payload = response.json()
        else:
            payload = response.text

        if response.ok:
            return {
                "ok": True,
                "status": response.status_code,
                "data": payload,
                "error": None,
            }

        return {
            "ok": False,
            "status": response.status_code,
            "data": payload,
            "error": f"HTTP {response.status_code}",
        }
    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "status": None,
            "data": None,
            "error": str(e),
        }
