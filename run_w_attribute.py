import copy
import math
from utilize.utilze import load_data, write_file
import tiktoken
import multiprocessing
from model.base import TMDBTools, SpotifyTools, Base
import argparse
from model.engine import PythonExecNet
from tqdm import tqdm
import re
import os

encoder = tiktoken.encoding_for_model('gpt-3.5-turbo')


def multi_process_func(ranks, func, data, model_name, dataset, oas_spec, n):
    pools = multiprocessing.Pool(processes=len(ranks))
    length = math.ceil(len(data) // len(ranks))
    collects = []
    for ids, rank in enumerate(ranks):
        collect = data[ids * length:(ids + 1) * length]
        collects.append(pools.apply_async(func, (rank, collect, model_name, dataset, oas_spec, n)))
    pools.close()
    pools.join()
    results = []
    for rank, result in zip(ranks, collects):
        r, res = result.get()
        assert r == rank
        results.extend(res)
    return results


def run(rank, data, model_name, dataset, oas_spec, n, folder):
    if dataset == 'tmdb':
        toolsets = TMDBTools(
            system='Here are some APIs used to access the TMDB platform. You need to answer the question by writing python code to call appreciate APIs and `print` the final answer. The API can be accessed via HTTP request. ',
            oas_spec=oas_spec,
        )
    elif dataset == 'spotify':
        toolsets = SpotifyTools(
            system='Here are some APIs used to access the Spotify platform. You need to answer the question by writing python code to call appreciate APIs and `print` the final answer. The API can be accessed via HTTP request. ',
            oas_spec=oas_spec,
        )
    else:
        raise NotImplemented

    results = []

    model = Base(model_name=model_name)
    env = PythonExecNet(dataset)

    bar = tqdm(data)
    cnt = 0
    for num, line in enumerate(bar):
        tools = copy.deepcopy(line['api_list'])
        instruction = toolsets.get_instruction(line['query'], tools, execution_results_type='_responses_json')
        line['code'], line['usage'], line['state'] = [], [], []

        print(len(encoder.encode(instruction)))
        if len(encoder.encode(instruction)) > 13000:
            continue

        messages = [{"role": "user", 'content': instruction}]

        try:
            for i in range(0, n):
                code, usage = model.generate(messages=messages)
                res, state = env.run(code)
                line['code'].append(code)
                line['usage'].append(usage)
                line['state'].append(state)

                if state == 0:
                    print(res)
                    cnt += 1
                    break

                print(f'### 1 {line["query"]} -> {res} *********')
                docs = [f'{i}. ' + toolsets.formulate(tool, is_description=True, is_parameters=False, is_request_type=False, is_request_body=False, is_url=True, execution_results_type=None)
                        for i, tool in enumerate(tools, start=1)]
                docs = '\n\n'.join(docs)
                matches = re.findall(r"```python(.*?)```", code, re.DOTALL)

                instruction = """In this task, you are a code reviewer. You should read my code and the error message to identify the reason for my bug.
Specifically, my code is to call the following APIs to solve the question: "{question}". Here are the details of the APIs.
{docs}

However, my code encounters the bug:
My code: ```python
{code}
```
The bug is:
=================
{bug}.
=================

Please help me to analyze my code and attribute the error message to the specific APIs callings. Note that you should select the tool name that triggers the error from the above tool list as your output.

Your output: [the tool name]""".format(question=line['query'], docs=docs, bug=res,
                                       code=copy.deepcopy(code) if matches == [] else matches[0].replace('```python', '').replace('[Python code]', ''))

                tool_name, _ = model.generate(messages=[{"role": 'user', 'content': instruction}])
                tool_name = [t for t in line['api_list'] if t in tool_name]
                print(f'###1 attribute -> {tool_name}************')
                if tool_name != []:
                    feedback = f"""Your code encountered an error (bug) during runtime, and the specific error message is as follows:
============
{res}
============

The error is potentially trigger in calling API: "{tool_name}". Please fix your bug and give the correct code:
```python
[Python code]
```"""
                else:  # state==2
                    print(f'###2 {line["query"]} -> {res} *********')
                    feedback = f"""The API calling is invalid since the execution result is
============
{res}
============

You can rethink the parameter passing to the API and please revise your code:
```python
[Python code]
```"""

                messages.append({"role": "assistant", "content": code})
                messages.append({"role": "user", "content": feedback})

        except Exception as e:
            print(e)

        bar.set_postfix({"success": cnt / (num + 1), 'item': cnt}, refresh=True)
        results.append(line)
        if folder != None:
            file = os.path.join(folder, line['qid'] + '.json')
            write_file(line, file)

    return rank, results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='gpt-3.5-turbo-16k-0613', choices=['Meta-Llama-3-8B-Instruct'])
    parser.add_argument('--n', type=int, default=1)
    parser.add_argument('--dataset', type=str, default='tmdb', choices=['spotify', 'tmdb', 'weather'])
    parser.add_argument('--data_file', type=str, default='./dataset/tmdb.data.candidate=20.v2.json',
                        choices=['./dataset/tmdb/tmdb.data.candidate=20.v2.json', ])
    parser.add_argument('--oas_spec', type=str, help='your data file containing the test examples and tools',
                        default='./dataset/tmdb/tmdb.spec.topo.v2.json', choices=['./dataset/tmdb/tmdb.spec.raw.v1.json', ])
    parser.add_argument('--folder', type=str,
                        default='./logs/tmdb/gpt3.5', choices=['./logs/tmdb/gpt3.5', ])

    args = parser.parse_args()

    data = load_data(args.data_file)

    indexes = []
    for file in os.listdir(args.folder):
        idx = file.replace('q', '').replace('.json', '')
        if idx.isdigit():
            indexes.append(int(idx))
    data = [e for i, e in enumerate(data) if i not in indexes]

    _, results = run(rank=0, data=data, model_name=args.model_name, dataset=args.dataset, oas_spec=args.oas_spec, n=args.n, folder=args.folder)
