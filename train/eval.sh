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
    --evaluate_only \
    --block_size=16384 \
    --per_device_train_batch_size=1 \
    --per_device_eval_batch_size=1 \
    --gradient_accumulation_steps=${grad_acc} \
    --fsdp="full_shard auto_wrap" \
    --fsdp_config="fsdp_config_qwen.json" \
    --bf16=True \
    --eval_strategy="no" \
    --logging_steps=1 \
    --gradient_checkpointing=True \
