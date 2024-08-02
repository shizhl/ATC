import copy
import re
import json
import execnet
import os
import spotipy


def _simplify_json(raw_json: dict):
    if isinstance(raw_json, dict):
        for key in raw_json.keys():
            raw_json[key] = simplify_json(raw_json[key])
        return raw_json
    elif isinstance(raw_json, list):
        if len(raw_json) == 0:
            return raw_json
        else:
            return [_simplify_json(raw_json[0])]
    else:
        return type(raw_json).__name__


def simplify_json(raw_json: dict):
    return _simplify_json(copy.deepcopy(raw_json))

def get_yaml(value, name, indent=0):
    result = ['\t' * indent + f"- {name}: {type(value).__name__}"]
    if list == type(value):
        element = f'{name}[0]'
        indent += 1
        if value != []:
            result.extend(get_yaml(value[0], element, indent))

    elif dict == type(value):
        for k, v in value.items():
            result.extend(get_yaml(v, k, indent + 1))
    return result


class PythonExecNet:

    def __init__(self, headers):
        self.headers = headers

    @staticmethod
    def judge(response):
        if response == None:
            return 0

        if type(response) == str:
            for e in ['"success":false','No keywords found', 'not available', 'No results found', 'out of range','is not subscriptable','Exception Value','is not defined',"n't exist",'could not be found','not be found']:
                if e.lower() in response.lower():
                    return 0
            tmp = copy.deepcopy(response.split())
            tmp = [e.lower() for e in tmp]
            for e in ['error', 'fail', '"error":', 'invalid', "n't"]: # 'None', '[]'
                if e.lower() in tmp:
                    return 0

        return 1

    def run(self, code,warp=False):
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, code, re.DOTALL)
        tmp = copy.deepcopy(code) if matches == [] else matches[0]
        tmp = tmp.replace('```python', '').replace('[Python code]', '').replace('```','').replace('``','')
        tmp = '\n'.join(['\t' + e for e in tmp.split('\n')])
        if warp == False:
            exec_code = f"""import sys
from io import StringIO
import requests
import json

old_stdout = sys.stdout
redirected_output = StringIO()
sys.stdout = redirected_output

headers = {self.headers}

try:
{tmp}
except Exception as e:
    error = ' Exception Type: '+ type(e).__name__
    error += ', Exception Value: ' + str(e)
    channel.send((str(error), False))
else:
    sys.stdout = old_stdout
    output = redirected_output.getvalue()
    channel.send((output, True))
"""
        else:
            tmp = tmp.replace('import requests','')
            exec_code = f"""import sys
from io import StringIO
import requests
import json
from collections import defaultdict
class Requests:
    def __init__(self):
        self.cnt = defaultdict(int)
        self.headers = {self.headers}

    def get(self, url, headers, params=None):
        import requests
        if params is None:
            response = requests.get(url, headers=self.headers)
        else:
            response = requests.get(url, headers=self.headers, params=params)

        self.cnt[url] += 1
        return response

    def put(self, url, data=None, **kwargs):
        import requests
        response = requests.put(url,data=data, **kwargs)
        self.cnt[url] += 1
        return response

    def post(self, url, data=None, json=None, **kwargs):
        import requests
        response = requests.post(url,data=data, json=json, **kwargs)
        self.cnt[url] += 1
        return response


    def delete(self, url, **kwargs):
        import requests
        response = requests.delete(url,**kwargs)
        self.cnt[url] += 1
        return response
    
    def count(self):
        res = []
        print('----------------------')
        for k, v in self.cnt.items():
            res.append(k + '->' + str(v))
        res = '###'.join(res)
        return res

# ##############
requests = Requests()

old_stdout = sys.stdout
redirected_output = StringIO()
sys.stdout = redirected_output

headers = {self.headers}
    
try:
{tmp}
except Exception as e:
    error = ' Exception Type: '+ type(e).__name__
    error += ', Exception Value: ' + str(e)
    channel.send((str(error), False))
else:
    print(requests.count())
    sys.stdout = old_stdout
    output = redirected_output.getvalue()
    channel.send((output, True))
"""
        try:
            gw = execnet.makegateway()
            channel = gw.remote_exec(exec_code)
            result, state = channel.receive()
        except Exception as e:
            state = False
            result = e

        result = str(result).strip()

        if state == False:
            return result, 1
        if state == True and PythonExecNet.judge(result) == 0:
            return result, 2

        return result, 0

