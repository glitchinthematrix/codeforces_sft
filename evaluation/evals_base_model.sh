#base model
MODEL_PATH="/root/hf/models/models--Qwen--Qwen2.5-7B/snapshots/d149729398750b98c0af14eb82c78cfe92750796/"

# lm_eval --model vllm --model_args pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,dtype=bfloat16,tensor_parallel_size=4 --tasks codeforces --batch_size auto --apply_chat_template --output_path /home/codeforces_sft/eval_outputs/base_model/ --log_samples --gen_kwargs "max_gen_toks=8192,temperature=0.7,top_p=0.8,do_sample=true,top_k=20" --limit 16
python3 grader.py --path /home/codeforces_sft/eval_outputs/base_model/