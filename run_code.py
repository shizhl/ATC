
import requests

# API: GET_search_person
url = "https://api.themoviedb.org/3/search/person"
params = {
    "query": "Sofia Coppola",
    "page": 1,
    "include_adult": True,
    "region": "US"
}

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwZGJhYjU5MGM3ZWFjYTA3ZWJlNjI1OTc0YTM3YWQ5MiIsInN1YiI6IjY1MmNmODM3NjYxMWI0MDBmZmM3MDM5OCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.McsK4Wm5XnRSDLn62Jhy787YUAwZcQz0X5qzkGuLe_s"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
person_id = data["results"][0]["id"] # the first result as Sofia Coppola

# Get movie credits for Sofia Coppola
# API: GET_person_person_id_movie_credits
url2 = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"

response2 = requests.get(url2, headers=headers)
data2 = response2.json()
movies_directed = []

for credit in data2["crew"]:
    if "director" in credit["job"].lower() or "directing" in credit["job"].lower():
        movies_directed.append(credit["title"])

number_of_movies_directed = len(movies_directed)

print(number_of_movies_directed)