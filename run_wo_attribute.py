import copy
import math
from utilize.utilze import load_data, write_file
import tiktoken
import multiprocessing
from model.base import TMDBTools, SpotifyTools, Base
import argparse
from model.engine import PythonExecNet
from tqdm import tqdm
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
    env = PythonExecNet(toolsets.headers)

    bar = tqdm(data)
    cnt = 0
    for num, line in enumerate(bar):
        tools = copy.deepcopy(line['api_list'])
        instruction = toolsets.get_instruction(line['query'], tools, execution_results_type='_responses_json')
        line['code'], line['usage'], line['state'] = [], [], []

        print(len(encoder.encode(instruction)))
        if len(encoder.encode(instruction)) > 15000:
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

        results.append(line)
        if folder != None:
            file = os.path.join(folder, line['qid'] + '.json')
            write_file(line, file)

    return rank, results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='gpt-3.5-turbo-16k-0613', choices=['Meta-Llama-3-8B-Instruct'])
    parser.add_argument('--n', type=int, default=3)
    parser.add_argument('--dataset', type=str, default='tmdb', choices=['spotify', 'tmdb', 'weather'])
    parser.add_argument('--data_file', type=str, default='./dataset/tmdb/tmdb.data.candidate=20.v2.json',
                        choices=['./dataset/tmdb/tmdb.data.candidate=20.v2.json', ])
    parser.add_argument('--oas_spec', type=str, help='your data file containing the test examples and tools',
                        default='/Users/shizhl/Documents/GitHub/ATC/dataset/tmdb/tmdb.spec.probed.v2.json')
    parser.add_argument('--folder', type=str,
                        default='./logs/tmdb/gpt3.5', choices=['./logs/tmdb/gpt3.5'])

    args = parser.parse_args()

    data = load_data(args.data_file)

    indexes = []
    for file in os.listdir(args.folder):
        idx = file.replace('q', '').replace('.json', '')
        if idx.isdigit():
            indexes.append(int(idx))
    data = [e for i, e in enumerate(data) if i not in indexes]

    _, results = run(rank=0, data=data, model_name=args.model_name, dataset=args.dataset, oas_spec=args.oas_spec, n=args.n, folder=args.folder)
