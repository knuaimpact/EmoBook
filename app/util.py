import torch

def get_device():
    if torch.backends.mps.is_available():
        return "mps"   # Mac GPU
    elif torch.cuda.is_available():
        return "cuda"
    return "cpu"