#!/bin/bash

conda activate sft
python3 download_dataset.py
python3 filtering.py
python3 decontamination.py
python3 tokenization.py
