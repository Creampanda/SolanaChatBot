import requests

# Base URL for the API
BASE_URL = "http://localhost:5001"
TOKEN_ADDRESS = "E5c1ZLiMkSt46W9tvWbSR6DMQRUpkxUpkEdLRcPr9akC"


def test_get_token_info_nonexistent():
    """Test retrieval of token info for a non-existent token"""
    response = requests.get(f"{BASE_URL}/get_token_info/nonexistent_token_address")
    assert response.status_code == 404, f"Error {response.text} \n {response.json()}"
    assert "not found" in response.json()["detail"], f"Error {response.text} \n {response.json()}"


def test_add_token():
    """Test adding a new token"""
    response = requests.post(f"{BASE_URL}/add_token/{TOKEN_ADDRESS}")
    assert response.status_code == 200, f"Error {response.text} \n {response.json()}"
    assert response.json()["address"] == TOKEN_ADDRESS, f"Error {response.text} \n {response.json()}"


def test_get_token_info_existent():
    """Test retrieval of token info for an existing token using a fixture"""
    response = requests.get(f"{BASE_URL}/get_token_info/{TOKEN_ADDRESS}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict), f"Error {response.text} \n {response.json()}"
    assert (
        data["pairs"][0]["baseToken"]["address"] == TOKEN_ADDRESS
    ), f"Error {response.text} \n {response.json()}"
