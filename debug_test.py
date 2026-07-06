import mlx.core as mx
try:
    a = mx.array([1, 2, 3])
    print(bool(a))
except Exception as e:
    print(e)
