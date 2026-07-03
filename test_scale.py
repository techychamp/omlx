import mlx.core as mx
import math

def get_llama_4_attn_scale(position_ids, beta, max_position_embeddings):
    scaling = 1 + beta * mx.log(1 + mx.floor(position_ids / max_position_embeddings))
    return mx.expand_dims(scaling, -1)
