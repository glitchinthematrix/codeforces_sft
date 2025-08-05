# Codeforces SFT

Fine-tuning pipeline for Codeforces competitive programming problems using Qwen 2.5 7B Instruct.

## Setup

Run the automated environment setup script:

```bash
chmod +x env_setup.sh
./env_setup.sh
conda activate sft
```

This installs:
- **PyTorch 2.5.1** with CUDA 12.4 support
- **Core ML packages**: transformers, datasets, accelerate, peft
- **Inference**: vLLM 0.7.3 for fast parallel inference  
- **Evaluation**: lm-eval 0.4.8 with dependencies
- **Utilities**: wandb, jupyter, matplotlib, seaborn

## Dataset Curation

The pipeline downloads, filters, decontaminates, and tokenizes Codeforces data:

```bash
cd data
chmod +x build_dataset.sh
./build_dataset.sh
```

This runs:
- `download_dataset.py` - Downloads raw Codeforces problems/solutions
- `filtering.py` - Filters by quality, difficulty, language
- `decontamination.py` - Removes potential test set contamination
- `tokenization.py` - Tokenizes for the target model

## Fine-tuning

Training uses FSDP across multiple GPUs with the Qwen 2.5 7B Instruct base model:

```bash
cd train
chmod +x train.sh
./train.sh
```

Key config:
- **Model**: Qwen 2.5 7B Instruct
- **Context**: 16K tokens
- **Batch size**: 1 per device, grad accumulation 2
- **Learning rate**: 3e-5 with cosine decay
- **Epochs**: 5
- **FSDP**: Full shard with auto wrap

Model saves to `/root/hf/models/codeforces_sft_qwen_2.5_7b_instruct_bs16_lr3e-5_epoch5_wd1e-4/`

## Evaluation

Evaluates the fine-tuned model on Codeforces problems with parallel scaling:

```bash
cd evaluation
chmod +x evals_sft_model_parallel.sh
./evals_sft_model_parallel.sh
```

Runs two configurations:
1. **Fixed thinking tokens**: `max_tokens_thinking=8192`
2. **Auto thinking tokens**: `max_tokens_thinking=auto`

Both use:
- **vLLM backend** with tensor parallelism (4 GPUs)
- **Generation**: 16K max tokens, temp=0.4, sampling enabled
- **Grading**: Automatic evaluation with `grader.py`

Results saved to `/home/codeforces_sft/eval_outputs/sft_model/`

## Directory Structure

```
├── data/
│   ├── build_dataset.sh      # Dataset pipeline
│   ├── download_dataset.py
│   ├── filtering.py
│   ├── decontamination.py
│   └── tokenization.py
├── train/
│   ├── train.sh              # Training script
│   ├── train.py
│   └── fsdp_config_qwen.json
└── evaluation/
    ├── evals_sft_model_parallel.sh  # Evaluation script
    └── grader.py
```
