import json
import sys
from openai import OpenAI
import time
import random

api_keys_list = [
'Add your OpenAI API'
]


def get_from_openai(model_name='gpt-3.5-turbo', api_key=None,
                    messages=None, prompt=None, stop=None, max_len=1000, temp=1, n=1,
                    json_mode=False, usage=False):
    for i in range(10):
        try:
            client = OpenAI(api_key=api_keys_list[random.randint(0, 100000) % len(api_keys_list)] if api_key is None else api_key,
                            base_url='https://api.chatanywhere.tech/v1')
            kwargs = {
                "model": model_name, 'max_tokens': max_len, "temperature": temp,
                "n": n, 'stop': stop,
            }
            if json_mode == True:
                kwargs['response_format'] = {"type": "json_object"}
            if 'instruct' in model_name and 'gpt' in model_name:
                # assert prompt != None or messages!=None
                kwargs['prompt'] = prompt if prompt != None else messages[0]['content']
                response = client.completions.create(**kwargs)
            else:
                assert messages is not None
                kwargs['messages'] = messages
                response = client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content if n == 1 else [res.message.content for res in response.choices]
            results = {"content": content}
            if usage == True:
                results['usage'] = [response.usage.completion_tokens, response.usage.prompt_tokens, response.usage.total_tokens]
            return results
        except:
            error = sys.exc_info()[0]
            print("API error:", error)
            time.sleep(120)
    return 'no response from openai model...'
