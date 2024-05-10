import requests


def get_token_info_from_dex(token_address: str) -> dict:
    """
    Fetch token information from the Dexscreener API.

    Args:
        token_address (str): The address of the token.

    Returns:
        dict: Token information retrieved from the Dexscreener API.
    """
    url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
    response = requests.get(url)
    data = response.json()
    return data
