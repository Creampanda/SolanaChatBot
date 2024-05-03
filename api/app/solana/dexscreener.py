import requests

from config import TOKEN


def get_token_info(token_address):
    url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
    response = requests.get(url)
    data = response.json()
    return data


# Пример использования
token_address = TOKEN
token_info = get_token_info(token_address)
print(token_info)
