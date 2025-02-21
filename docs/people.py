import requests

url = "https://nubela.co/proxycurl/api/v2/linkedin?url=https%3A%2F%2Flinkedin.com%2Fin%2Fjohnrmarty"

response = requests.get(url, headers=headers)

print(response.json())
