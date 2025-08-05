import datasets
import os

ds = datasets.load_dataset("open-r1/codeforces", cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='test')
ds_code = datasets.load_dataset("open-r1/Mixture-of-Thoughts", 'code', cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='train')
ds_math = datasets.load_dataset("open-r1/Mixture-of-Thoughts", 'math', cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='train')
