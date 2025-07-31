import os
# Fix tokenize.Name compatibility for pandas with Python 3.11+
import datasets


# os.environ['HF_DATASETS_DOWNLOADED_DATASETS_PATH'] = '~/hf/datasets'
# os.environ['HF_HOME'] = '~/hf/'
# os.environ['HF_DATASETS_CACHE'] = '~/hf/datasets'


def filter_code(ds_code, top_k=10000, max_tokens=16384):
    dataset_dict = {'question': [], 'thinking_trace': [], 'answer': [], 'num_tokens': [], 'source': []}
    # filter for items with num_tokens < max_tokens, then take top_k by num_tokens descending
    filtered_indices = [i for i in range(len(ds_code)) if ds_code[i]['num_tokens'] < max_tokens]
    sorted_indices = sorted(filtered_indices, key=lambda i: ds_code[i]['num_tokens'], reverse=True)
    selected_indices = sorted_indices[:top_k]
    for i in selected_indices:
        response = ds_code[i]['messages'][1]['content']
        if '<think>' not in response or '</think>' not in response:
            continue
        trace = response.split('<think>')[1].split('</think>')[0].strip()
        answer = response.split('</think>')[1].strip()
        
        dataset_dict['question'].append(ds_code[i]['messages'][0]['content'])
        dataset_dict['thinking_trace'].append(trace)
        dataset_dict['answer'].append(answer)
        dataset_dict['num_tokens'].append(ds_code[i]['num_tokens'])
        dataset_dict['source'].append(ds_code[i].get('source', ''))

    return datasets.Dataset.from_dict(dataset_dict)


def main():
    ds_code = datasets.load_dataset("open-r1/Mixture-of-Thoughts", 'code', cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='train')
    ds_code_filtered = filter_code(ds_code,40000)
    ds_math = datasets.load_dataset("open-r1/Mixture-of-Thoughts", 'math', cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='train')
    ds_math_filtered = filter_code(ds_math,10000)
    ds_combined = datasets.concatenate_datasets([ds_code_filtered, ds_math_filtered])
    #save to disk
    ds_combined.save_to_disk('~/hf/datasets/sft_filtered/')
    
   


if __name__ == "__main__":
    main()