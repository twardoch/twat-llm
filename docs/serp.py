import requests

url = "https://webknox-search.p.rapidapi.com/media/images/search"

querystring = {"keyword":"fontlab"}

headers = {
	"x-rapidapi-key": "fbc450445amshee120728b154b67p1505e8jsn9bdde3f1ea1d",
	"x-rapidapi-host": "webknox-search.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
