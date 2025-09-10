import requests
import logging

logger = logging.getLogger(__name__)

class FiveSimAPI:
    def __init__(self, api_key):
        self.base_url = "https://api-jack.ml/api-5sim"
        self.api_key = api_key

    def _make_request(self, endpoint, params=None):
        """Helper function to make requests to the API."""
        if params is None:
            params = {}
        params['key'] = self.api_key

        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            # The API returns plain text or text with colons, not always JSON
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling 5sim API endpoint {endpoint}: {e}")
            return None

    def get_balance(self):
        """Gets the current balance."""
        # The PHP code uses a regex to filter, let's just get the raw text
        return self._make_request("coin")

    def get_prices_by_country(self, country):
        """Gets number prices for a specific country."""
        # This endpoint is guessed from the PHP code `get?key=...&country=...`
        return self._make_request("get", {"country": country})

    def purchase_number(self, country, app):
        """Purchases a new number."""
        # Endpoint guessed from `get_num?key=...&apps=...&country=...`
        response_text = self._make_request("get_num", {"country": country, "apps": app})
        if not response_text:
            return None

        # The PHP code expects a colon-separated string like "ID:12345:NUMBER"
        parts = response_text.replace('"', '').split(':')
        if len(parts) >= 3:
            return {"id": parts[1], "number": parts[2]}
        return {"error": response_text}


    def get_sms_code(self, purchase_id):
        """Checks for the SMS code for a given purchase ID."""
        response_text = self._make_request("code", {"id": purchase_id})
        if not response_text:
            return None

        # Response can be "STATUS_WAIT_CODE" or "STATUS_OK:12345"
        return {"raw": response_text}

    def ban_number(self, purchase_id):
        """Reports a number as banned."""
        return self._make_request("band", {"id": purchase_id})
