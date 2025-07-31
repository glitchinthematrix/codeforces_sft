run_name="codeforces_sft_qwen_2.5_7b_instruct_bs16_lr3e-5_epoch5_wd1e-4"

if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
    gpu_count=$(nvidia-smi -L | wc -l)
else
    gpu_count=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l)
fi

echo "GPU count: $gpu_count"

nnodes=1
grad_acc=2
head_node_ip="127.0.0.1"

torchrun \
    --nnodes=$nnodes \
    --nproc_per_node=$gpu_count \
    --rdzv_id=0 \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$head_node_ip:29500 \
    train.py \
    --block_size=16384 \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --gradient_accumulation_steps=${grad_acc} \
    --num_train_epochs=5 \
    --train_dataset_name="sft_open_r1" \
    --model_name=qwen_2.5_7b_instruct \
    --warmup_ratio=0.05 \
    --report_to="wandb" \
    --fsdp="full_shard auto_wrap" \
    --fsdp_config="fsdp_config_qwen.json" \
    --bf16=True \
    --save_strategy="epoch" \
    --eval_strategy="no" \
    --logging_steps=1 \
    --lr_scheduler_type="cosine" \
    --learning_rate=3e-5 \
    --weight_decay=1e-4 \
    --adam_beta1=0.9 \
    --adam_beta2=0.95 \
    --output_dir="/root/hf/models/${run_name}" \
    --push_to_hub=false \
    --save_only_model=True \
    --gradient_checkpointing=True \
