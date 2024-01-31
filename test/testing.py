import requests

# The base URL where your Flask application is running
BASE_URL = 'http://127.0.0.1:5000'

def create_paste_api(content):
    """Create a new paste via the API."""
    url = f'{BASE_URL}/api/paste'
    response = requests.post(url, json={'content': content})
    if response.status_code == 201:
        print("Paste created successfully:", response.json())
        return response.json()['id']
    else:
        print("Failed to create paste:", response.json())

def get_paste_api(paste_id):
    """Retrieve an existing paste via the API."""
    url = f'{BASE_URL}/api/paste/{paste_id}'
    response = requests.get(url)
    if response.status_code == 200:
        print("Paste retrieved successfully:", response.json())
    else:
        print("Failed to retrieve paste:", response.json())

if __name__ == '__main__':
    print("Testing API...")
    # Test creating a new paste
    new_paste_id = create_paste_api("This is a test paste from the CLI.")
    if new_paste_id:
        # Test retrieving the newly created paste
        get_paste_api(new_paste_id)