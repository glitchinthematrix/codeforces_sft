import json
import datasets
from transformers import AutoTokenizer
from argparse import ArgumentParser
from functools import partial
import os
import random
# Set Huggingface cache directory
os.environ['HUGGINGFACE_HUB_CACHE'] = '/root/hf/'



def ApplyTemplate(item, tokenizer):

    prompt = item['question'] 
    cot = item['thinking_trace']
    answer = item['answer']

    text = tokenizer.apply_chat_template([
        {"role": "user", "content": prompt.strip()},
        {
            "role": "assistant", 
            "content": "<|im_start|>think\n" + cot.strip() + "\n<|im_start|>answer\n" + answer.strip()
        }
    ], tokenize=False)

    return dict(text=text)

def tokenize_fn(example, tokenizer):
    return {**tokenizer(
        example['text'],
        padding=False
    ),'text': example['text']}

def main(args):
    # load tokenizer from cache
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct", cache_dir='/root/hf/', use_fast=True)
    ds = datasets.load_from_disk(args.decontaminated_ds_path)
    print('loaded dataset')
    ds = ds.map(partial(ApplyTemplate, tokenizer=tokenizer))
    ds = ds.map(partial(tokenize_fn, tokenizer=tokenizer), batched=True, num_proc=8)
    dataset_w_split = datasets.DatasetDict({'train': ds})

    # display the first 5 examples
    for i in range(5):
        print(dataset_w_split['train'][i]['text'])
        print('*'*100)
    dataset_w_split.save_to_disk(f"/root/hf/datasets/sft_filtered_decontaminated_tokenized/")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--decontaminated_ds_path", type=str, default="/root/hf/datasets/sft_filtered_decontaminated/")
    args = parser.parse_args()
    main(args)