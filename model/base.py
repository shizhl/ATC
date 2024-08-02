import copy
import json
from utilize.apis import get_from_openai
import spotipy
import yaml
import os
import tiktoken
from model.instruction import *


encoder = tiktoken.encoding_for_model('gpt-3.5-turbo')

def simplify_response_template(data):
    if 'required' in data and 'properties' in data:
        for k, v in data['properties'].items():
            if k not in data['required']:
                data.pop(k)
    if 'type' in data and data['type'] == 'object' and 'properties' in data:
        for k, v in data['properties'].items():
            data['properties'][k] = simplify_response_template(v)
    else:
        for k, v in data.items():
            if k in ['example', 'nullable', 'x-spotify-docs-type']:
                data.pop(k)
            if k == 'description':
                data[k] = normalize(v)
    return data


def simplify_spec(data):
    """
    Recursively simplify the dictionary by removing specific keys.

    :param data: The input dictionary to be simplified.
    :return: A simplified dictionary with specified keys removed.
    """
    keys_to_remove = ['example', 'nullable', 'x-spotify-docs-type', 'required', 'default', 'minimum', 'maximum', 'examples']

    if isinstance(data, dict):
        results = {}
        for k, v in data.items():
            if k in keys_to_remove:
                continue
            # if k == 'description':
            #     results[k] = normalize(simplify_spec(v))
            # else:
            results[k] = simplify_spec(v)
        return results
    elif isinstance(data, list):
        return [simplify_spec(item) for item in data]
    else:
        if type(data) == str:
            return normalize(data)
        return data


def normalize(sss):
    for s in ['<br />', '<br/>', '_**NOTE**:']:
        sss = sss.replace(s, '\n')
    sss = sss.split('\n')[0]
    tmp = [
        '(/documentation/web-api/#spotify-uris-and-ids)',
        '(https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)',
        '(https://www.spotify.com/se/account/overview/)',
        '(http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)',
        '<br/>',
        '<br>',
        '<br />',
        '\n',
        '/documentation/general/guides/track-relinking-guide/',
        '(http://en.wikipedia.org/wiki/Universal_Product_Code)',
        '(http://en.wikipedia.org/wiki/International_Standard_Recording_Code)',
        '/documentation/web-api/#spotify-uris-and-ids'
    ]
    for s in tmp:
        sss = sss.replace(s, '')

    for i in range(10):
        sss = sss.replace(f'[{i}].', '')
        sss = sss.replace(f'[{i}]', '')
    return sss.strip()


class Base:

    def __init__(self, model_name='gpt-3.5-turbo'):
        self.model_name = model_name
        self.token = []

    def normalize(self, sss):
        return sss

    def generate(self, messages):
        res = get_from_openai(model_name=self.model_name, messages=messages, usage=True)
        self.token.append(res['usage'])
        return self.normalize(res['content']), res['usage']

    def get_token(self):
        tmp = []
        for line in self.token:
            tmp = [e1 + e2 for e1, e2 in zip(tmp, line)]
        return tmp


class Tool:
    def __init__(self, spec: dict):

        self.name = spec['name']
        self.method = spec['method']
        self.url = spec['url']
        self.description = spec['description']
        self.parameter = spec['parameters'] if 'parameters' in spec else []
        self.responses = {}

        if 'requestBody' in spec and spec['requestBody'] != None:
            self.requestBody = simplify_spec(spec['requestBody']['content']['application/json']["schema"]['properties'])
        else:
            self.requestBody = 'This API do not need the request body when calling.'

        if 'responses' in spec and spec['responses'] is not None and 'content' in spec['responses']:
            self.responses['responses'] = simplify_spec(spec['responses']['content']['application/json']["schema"]['properties'])
            self.responses['responses'] = json.dumps(self.responses['responses'], indent=4)
        else:
            self.responses['responses'] = 'This API has no return value.'

        if '_responses_json' in spec and spec['_responses_json'] is not None:
            self.responses['_responses_json'] = json.dumps(spec['_responses_json'], indent=4) if type(spec['_responses_json']) == dict else spec['_responses_json']
        else:
            self.responses['_responses_json'] = None

    def update_response(self, response_format, response_example):
        if response_format == '_response_yaml':
            self.responses[response_format] = response_example
        else:
            self.responses[response_format] = response_example if type(response_example) == str else json.dumps(response_example, indent=4)

    def get_parameters(self) -> str:
        if len(self.parameter) == 0:
            parameter = 'No extra parameter, just replace the `{variable}` in the url path with actual value.'
        else:
            parameter = []
            for p in self.parameter:
                tmp = "- " + p['name'] + ": " + normalize(p['description'])
                if 'schema' in p and 'type' in p['schema']:
                    tmp += " (type: " + p['schema']['type'] + ")"
                parameter.append(tmp)
            parameter = '\n'.join(parameter)
            if '{' in self.url:
                parameter += '\nThe `{variable}` in the url path should also be replaced with actual value.'
        return parameter

    def formulate(self, is_description=True, is_parameters=True, is_request_type=True, is_url=True,
                  execution_results_type=None, is_request_body=True):
        text_doc = ["""API name: """ + self.name]
        if is_url:
            text_doc.append('### API url\n' + self.url)
        if is_request_type:
            method = """### Request type\n""" + self.method
            text_doc.append(method)
        if is_description:
            description = """### Description\n""" + normalize(self.description)
            text_doc.append(description)
        if is_parameters:
            parameters = '### Parameter\n' + self.get_parameters()
            text_doc.append(parameters)
        if execution_results_type is not None and execution_results_type in self.responses:
            response = '### Execution result specification\n' + str(self.responses[execution_results_type])
            text_doc.append(response)
        if is_request_body:
            requestBody = '### Request body\n' + json.dumps(self.requestBody, indent=4)
            text_doc.append(requestBody)
        text_doc = '\n'.join(text_doc)
        return text_doc


class Tools:

    def __init__(self, system, oas_spec):
        self.system = system
        api_spec = json.load(open(oas_spec))
        self.endpoint = {e['name']: Tool(e) for e in api_spec['endpoints']}
        self.host = api_spec['servers'][0]['url'] if 'servers' in api_spec else None
        self.headers = api_spec['headers']
    def match(self, name):
        return name

    def get_tool_list(self):
        tmp = [k for k, v in self.endpoint.items()]
        return tmp

    def formulate(self, tool, is_description=True, is_parameters=True, is_request_type=True, is_url=True,
                  execution_results_type=None, is_request_body=True):
        tool = self.match(tool)
        doc = self.endpoint[tool].formulate(is_description=is_description,
                                            is_parameters=is_parameters, is_url=is_url,
                                            execution_results_type=execution_results_type,
                                            is_request_type=is_request_type, is_request_body=is_request_body)
        return doc


class TMDBTools(Tools):

    def __init__(self, system, oas_spec):
        super(TMDBTools, self).__init__(system=system, oas_spec=oas_spec)

    def get_instruction(self, query, tools,
                        is_description=True,
                        is_parameters=True,
                        is_request_type=True,
                        execution_results_type='responses',
                        is_request_body=True,
                        is_url=True):
        docs = [f'{i}. ' + self.formulate(tool, is_description=is_description,
                                          is_parameters=is_parameters,
                                          is_request_body=is_request_body, is_url=is_url,
                                          execution_results_type=execution_results_type,
                                          is_request_type=is_request_type)
                for i, tool in enumerate(tools, start=1)]

        instruction = GPT_TMDB_INSTRUCTION.format(system=self.system,headers=json.dumps(self.headers, indent=4), query=query, docs='\n\n'.join(docs))
        return instruction


class SpotifyTools(Tools):

    def __init__(self, system, oas_spec):
        super(SpotifyTools, self).__init__(system=system, oas_spec=oas_spec)
        config = yaml.load(open('YOUR_SPOTIFY_CONFIG.yaml', 'r'), Loader=yaml.FullLoader)
        os.environ['SPOTIPY_CLIENT_ID'] = config['spotipy_client_id']
        os.environ['SPOTIPY_CLIENT_SECRET'] = config['spotipy_client_secret']
        os.environ['SPOTIPY_REDIRECT_URI'] = config['spotipy_redirect_uri']
        with open("YOUR_SPOTIFY_CONFIG_OAS.json") as f:
            raw_api_spec = json.load(f)
        scopes = list(
            raw_api_spec['components']['securitySchemes']['oauth_2_0']['flows']['authorizationCode'][
                'scopes'].keys())
        access_token = spotipy.util.prompt_for_user_token(scope=','.join(scopes))
        self.headers = {
            'Authorization': f'Bearer {access_token}'
        }

    def get_instruction(self,  query, tools,
                        is_description=True,
                        is_parameters=True,
                        is_request_type=True,
                        execution_results_type='responses',
                        is_request_body=True,
                        is_url=True):
        docs = [f'{i}. ' + self.formulate(tool, is_description=is_description,
                                          is_parameters=is_parameters,
                                          is_request_body=is_request_body, is_url=is_url,
                                          execution_results_type=execution_results_type,
                                          is_request_type=is_request_type)
                for i, tool in enumerate(tools, start=1)]

        instruction = GPT_SPOTIFY_INSTRUCTION.format(system=self.system, headers=json.dumps(self.headers, indent=4), query=query, docs='\n'.join(docs))

        return instruction

class RapidTools(Tools):

    def __init__(self, system, oas_spec):
        super(RapidTools, self).__init__(system=system, oas_spec=oas_spec)
        self.headers = {
            'X-RapidAPI-Key': 'YOUR_KEY',
            'X-RapidAPI-Host': 'ai-weather-by-meteosource.p.rapidapi.com'
        }
    def get_instruction(self, query, tools,
                        is_description=True,
                        is_parameters=True,
                        is_request_type=True,
                        execution_results_type='responses',
                        is_request_body=True,
                        is_url=True):
        docs = [f'{i}. ' + self.formulate(tool, is_description=is_description,
                                          is_parameters=is_parameters,
                                          is_request_body=is_request_body, is_url=is_url,
                                          execution_results_type=execution_results_type,
                                          is_request_type=is_request_type)
                for i, tool in enumerate(tools, start=1)]

        instruction = """Here are some APIs used to access the Open Weather platform. You need to answer the question by writing python code to call appreciate APIs and `print` the final answer. The API can be accessed via HTTP request. 

Here are the OpenAPI Specification of given APIs, including their http url, description, arguments and execution results.
{docs}

You should use the following Http headers to call the API:
```python
headers = {headers}
```
Note: I will give you the `headers` used to request the http server. Do not make up one in your code. Here is an example to request the API:
```python
import requests
url = "<The API url selected from the above APIs>"
params = "<The params dict>"
response = requests.get(url, headers=headers, params=params) # The variable `headers` has been defined, please JUST USE it.
```
If the API path contains "{{}}", it means that it is a variable and you should replace it with the appropriate value. For example, if the path is "/users/{{user_id}}/tweets", you should replace "{{user_id}}" with the user id. "{{" and "}}" cannot appear in the url.

Based on provided APIs, please write python code to call API and solve it. Try to write correct Python Code and avoid grammar error, e.g. `variable is not defined`.  You need to provide Python code that can be executed directly; Please add the name of the used APIs in Python comments for the attributable consideration. 

**Note**: any information, e.g., person id or movie id, you need to obtain it by calling appropriate APIs. DO NOT make up value by yourself!

Query: {query}
Your output:
```python
headers = {headers}
Complete the python code...
```""".format(headers=json.dumps(self.headers, indent=4), query=query, docs='\n\n'.join(docs))

        return instruction

