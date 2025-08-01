'''
Adapted from https://github.com/simplescaling/s1/blob/main/train/sft.py
'''

import os
from dataclasses import dataclass, field, asdict
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from datasets import load_from_disk
import transformers
import trl
import argparse


@dataclass
class EvaluationConfig:
    block_size: int = field(default=16384)
    checkpoint_path: str = field(default="/root/hf/models/codeforces_sft_qwen_2.5_7b_instruct_bs16_lr3e-5_epoch5_wd1e-4/")
    val_dataset_path: str = field(default="/root/hf/datasets/sft_filtered_decontaminated_tokenized/")


@dataclass
class TrainingConfig:
    model_name: str = field(default="qwen_2.5_7b_instruct")
    block_size: int = field(default=16384)
    wandb_project: str = field(default="codeforces_sft")
    wandb_entity: str = field(default="glitchinthematrix")
    train_dataset_name: str = field(default="sft_open_r1")
    train_dataset_path: str = field(default="/root/hf/datasets/sft_filtered_decontaminated_tokenized/")
    cache_dir: str = field(default="/root/hf/models/")
    dagger: bool = field(default=False)

    def __post_init__(self):
        os.environ['WANDB_PROJECT'] = self.wandb_project
        os.environ['WANDB_ENTITY'] = self.wandb_entity
        os.environ['WANDB_DIR'] = '/home/codeforces_sft/wandb_logs'
        
        if self.train_dataset_name == "sft_open_r1":
            self.train_dataset_path = "/root/hf/datasets/sft_filtered_decontaminated_tokenized/"
        else:
            raise ValueError(f"Train dataset name {self.train_dataset_name} not supported")

def evaluate():
    parser = transformers.HfArgumentParser((EvaluationConfig, trl.SFTConfig))
    config, args = parser.parse_args_into_dataclasses()
    log_config = {**asdict(config), **asdict(args)}
    logging.info(f"Evaluation config: {log_config}")

    ckpt_list = [d for d in os.listdir(config.checkpoint_path) if 'checkpoint' in d]
    if len(ckpt_list) == 0:
        raise ValueError(f"No checkpoints found in {config.checkpoint_path}")
    for ckpt in ckpt_list:
        model_path = os.path.join(config.checkpoint_path, ckpt)
        model = transformers.AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_path)
        dataset = load_from_disk(config.val_dataset_path)
        instruction_template = "<|im_start|>user\n"
        response_template = "<|im_start|>assistant\n"
        tokenizer.add_special_tokens({'pad_token': '<|fim_pad|>'})
        collator = trl.DataCollatorForCompletionOnlyLM(
            response_template=response_template,
            tokenizer=tokenizer,
            mlm=False,
            instruction_template=instruction_template
        )
        args.dataset_text_field = 'text'
        args.max_seq_length = config.block_size
        
        # Set up trainer for evaluation
        trainer = trl.SFTTrainer(
            model,
            train_dataset=None,
            eval_dataset=dataset['test'] if 'test' in dataset else None,
            args=args,
            data_collator=collator,
            peft_config=None,
        )
        
        if 'test' in dataset:
            logging.info(f"Evaluating checkpoint: {ckpt}")
            eval_results = trainer.evaluate()
            logging.info(f"Evaluation results for {ckpt}: {eval_results}")
        else:
            logging.warning("No test split found in dataset, skipping evaluation")
            break
    
    
def train():
    # parsing input
    parser = transformers.HfArgumentParser((TrainingConfig, trl.SFTConfig))
    config, args = parser.parse_args_into_dataclasses()
    log_config = {**asdict(config), **asdict(args)}
    logging.info(f"Training config: {log_config}")
    
            
    if config.model_name == "qwen_2.5_7b_instruct":
        model_path = os.path.join(config.cache_dir, "models--Qwen--Qwen2.5-7B-Instruct")
        model_path = os.path.join(model_path, 'snapshots/')
        # Get latest snapshot hash
        if os.path.exists(model_path):
            snapshots = [d for d in os.listdir(model_path) if os.path.isdir(os.path.join(model_path, d))]
            if snapshots:
                latest = sorted(snapshots)[-1]  
                model_path = os.path.join(model_path, latest)
            else:
                raise ValueError(f"No snapshots found in {model_path}")
            
    else:
        raise ValueError(f"Model name {config.model_name} not supported")
    
   
       
    dataset = load_from_disk(config.train_dataset_path)

    # setting up trainer
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_path, use_fast=True)
    model = transformers.AutoModelForCausalLM.from_pretrained(model_path)

    instruction_template = "<|im_start|>user\n"
    response_template = "<|im_start|>assistant\n"
    # Use a token that is never used
    tokenizer.add_special_tokens({'pad_token': '<|fim_pad|>'})

    # Only compute loss over assistant responses
    # Verified that it precisely starts where the thinking tokens start and ends with the first pad token
    # via labels being set to -100
    collator = trl.DataCollatorForCompletionOnlyLM(
        response_template=response_template,
        tokenizer=tokenizer,
        mlm=False,
        instruction_template=instruction_template
    )
    args.dataset_text_field = 'text'
    args.max_seq_length = config.block_size
    
    trainer = trl.SFTTrainer(
        model,
        train_dataset=dataset['train'],
        eval_dataset=dataset['test'] if 'test' in dataset else dataset['train'],
        args=args,
        data_collator=collator,
        peft_config=None,
    )

    trainer.train()
    trainer.save_model(output_dir=args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    trainer.accelerator.wait_for_everyone()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate_only", action="store_true")
    args = parser.parse_args()
    if args.evaluate_only:
        evaluate()
    else:
        train()

   