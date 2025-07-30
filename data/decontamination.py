import datasets
import json
from argparse import ArgumentParser
from decontamination_utils import *


def main(args):


    sft_data = datasets.load_from_disk(args.train_ds_path)
    sft_text = [row['question'] + row['thinking_trace'] + row['answer'] for row in sft_data]

    test_dataset = datasets.load_dataset("open-r1/codeforces",  cache_dir="~/hf/datasets", download_mode='reuse_dataset_if_exists',split='test')
    test_text = [row['description'] for row in test_dataset]
 
    test_lookup = build_ngram_lookup(test_text, ngram_size=args.ngram_size)
    train_lookup = build_ngram_lookup(sft_text, ngram_size=args.ngram_size)
    contaminated_ids = find_contaminated_questions(train_lookup, test_lookup)

    print("Original number of train questions:", len(sft_data))
    print("Number of contaminated questions:", len(contaminated_ids))

    # Remove contaminated rows and save cleaned dataset
    keep_indices = [i for i in range(len(sft_data)) if i not in contaminated_ids]
    cleaned_sft_data = sft_data.select(keep_indices)
    cleaned_sft_data.save_to_disk(args.train_ds_path.rstrip('/') + "_decontaminated/")
    print(f"Saved decontaminated dataset with {len(cleaned_sft_data)} rows to {args.train_ds_path.rstrip('/') + '_decontaminated/'}")

    # Save contaminated n-gram overlaps
    contaminated_overlaps = []
    for ngram, test_doc_ids in test_lookup.items():
        if ngram in train_lookup:
            contaminated_overlaps.append({
                'ngram': ngram,
                'test_doc_ids': list(test_doc_ids),
                'train_doc_ids': list(train_lookup[ngram])
            })
    
    overlaps_path = args.train_ds_path.replace("_filtered/", "_contaminated_overlaps.json")
    with open(overlaps_path, "w") as f:
        json.dump(contaminated_overlaps, f, indent=2)
    
    print(f"Saved contaminated n-gram overlaps to {overlaps_path}")


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--train_ds_path", type=str, default="/root/hf/datasets/sft_filtered/")
    parser.add_argument("--ngram_size", type=int, default=20)
    args = parser.parse_args()
    main(args)