#model path
MODEL_PATH="/root/hf/models/codeforces_sft_qwen_2.5_7b_instruct_bs16_lr3e-5_epoch5_wd1e-4/"
#parallel scaling with max_tokens_thinking=8192
lm_eval --model vllm --model_args pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,dtype=bfloat16,tensor_parallel_size=4,gpu_memory_utilization=0.9,max_model_len=16384 --tasks codeforces --batch_size auto --apply_chat_template --output_path /home/codeforces_sft/eval_outputs/sft_model/parallel_scaling --log_samples --gen_kwargs "max_gen_toks=16384,temperature=0.4,do_sample=true,max_tokens_thinking=8192" 
python3 grader.py --path /home/codeforces_sft/eval_outputs/sft_model/parallel_scaling/
#parallel scaling with max_tokens_thinking=auto
lm_eval --model vllm --model_args pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,dtype=bfloat16,tensor_parallel_size=4,gpu_memory_utilization=0.9,max_model_len=16384 --tasks codeforces --batch_size auto --apply_chat_template --output_path /home/codeforces_sft/eval_outputs/sft_model/parallel_scaling_2 --log_samples --gen_kwargs "max_gen_toks=16384,temperature=0.4,do_sample=true,max_tokens_thinking=auto" 
python3 grader.py --path /home/codeforces_sft/eval_outputs/sft_model/parallel_scaling_2/