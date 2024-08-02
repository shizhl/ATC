
GPT_TMDB_INSTRUCTION = """{system}
Here are the OpenAPI Specification of given APIs, including their http url, description, arguments and execution results.
{docs}

You should use the following Http headers to call the API:
```python
headers = {headers}
```
Note: I will give you 'headers', do not make up one, just reference it in your code. Here is an example to request the API:
```python
import requests
url = "<The API url selected from the above APIs>"
params = "<The params dict>"
response = requests.get(url, headers=headers, params=params) # The variable `headers` has been defined
```
If the API path contains "{{}}", it means that it is a variable and you should replace it with the appropriate value. For example, if the path is "/users/{{user_id}}/tweets", you should replace "{{user_id}}" with the user id. "{{" and "}}" cannot appear in the url.

Based on provided APIs, please write python code to call API and solve it. Try to write correct Python Code and avoid grammar error, e.g. `variable is not defined`.  You need to provide Python code that can be executed directly; Please add the name of the used APIs in Python comments for the attributable consideration. 
Note: you should be faithful to the question, please acquire any information you need by calling the APIs (e.g., person id or movie id). DO NOT make up value by yourself.

Query: {query}
Your output:
```python
[Please write the code]
```"""


GPT_SPOTIFY_INSTRUCTION = """{system}

Here are the OpenAPI Specification of given APIs, including their http url, description, arguments and execution results.
{docs}

You should use the following Http headers to call the API:
```python
headers = {headers}
```
**Note**: I have defined the 'headers' in python environment. Please just reference the pre-defined `headers` in your code. DO NOT make up one by your self!

Here is an example to request the API:
```python
import requests
url = "<The API url selected from the above APIs>"
params = "<The params dict>"
method = "<The Http request type, e.g., POST, GET, PUT and DELETE>"
if method == "GET":
    response = requests.get(url, headers=headers, params=params) # The variable `headers` has been defined, please JUST USE it.
elif method == "POST":
    request_body = "<The request body>"
    response = requests.post(url, headers=headers, params=params, data=request_body) # The variable `headers` has been defined, please JUST USE it.
elif method == "PUT":
    request_body = "<The request body>"
    response = requests.put(url, headers=headers, params=params, data=request_body) # The variable `headers` has been defined, please JUST USE it.
elif method == "DELETE":
    request_body = "<The request body>"
    response = requests.delete(url, headers=headers, params=params, json=request_body) # The variable `headers` has been defined, please JUST USE it.
```
If the API path contains "{{}}", it means that it is a variable and you should replace it with the appropriate value. For example, if the path is "/users/{{user_id}}/tweets", you should replace "{{user_id}}" with the user id. "{{" and "}}" cannot appear in the url.

Based on provided APIs, please write python code to call API and solve it. Try to write correct Python Code and avoid grammar error, e.g. `variable is not defined`.  You need to provide Python code that can be executed directly; Please add the name of the used APIs in Python comments for the attributable consideration. 
Note: you should be faithful to the question, please acquire any information you need by calling the APIs (e.g., person id or movie id). DO NOT make up value by yourself.

Query: {query}
Your output:
```python
[Please write the code]
```"""