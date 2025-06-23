import requests

url = "https://nubela.co/proxycurl/api/v2/linkedin?url=https%3A%2F%2Flinkedin.com%2Fin%2Fjohnrmarty"

# Define headers as None for this example, or provide actual headers if available
headers = None  # Or your actual headers dictionary
response = requests.get(url, headers=headers, timeout=10)

print(response.json())  # noqa: T201
