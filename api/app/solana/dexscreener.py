import requests


def get_token_info(token_address: str) -> dict:
    url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
    response = requests.get(url)
    data = response.json()
    return data
