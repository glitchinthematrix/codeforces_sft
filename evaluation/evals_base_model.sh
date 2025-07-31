#base model
MODEL_PATH="/root/hf/models/models--Qwen--Qwen2.5-7B-Instruct/snapshots/a09a35458c702b33eeacc393d103063234e8bc28/"
lm_eval --model vllm --model_args pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,dtype=bfloat16,tensor_parallel_size=4 --tasks codeforces --batch_size auto --apply_chat_template --output_path /home/codeforces_sft/eval_outputs/base_model/ --log_samples --gen_kwargs "max_gen_toks=8192,temperature=0.7,top_p=0.8,do_sample=true,top_k=20" 

#coder instruct
# MODEL_PATH="/root/hf/models/models--Qwen--Qwen2.5-Coder-7B-Instruct/snapshots/c03e6d358207e414f1eca0bb1891e29f1db0e242"
# lm_eval --model vllm --model_args pretrained=$MODEL_PATH,tokenizer=$MODEL_PATH,dtype=bfloat16,tensor_parallel_size=4 --tasks codeforces --batch_size auto --apply_chat_template --output_path /home/codeforces_sft/eval_outputs/coder_model/ --log_samples --gen_kwargs "max_gen_toks=8192,temperature=0.7,top_p=0.9,do_sample=true" 


# python3 grader.py --path /home/codeforces_sft/eval_outputs/base_model/
# python3 grader.py --path /home/codeforces_sft/eval_outputs/coder_model/