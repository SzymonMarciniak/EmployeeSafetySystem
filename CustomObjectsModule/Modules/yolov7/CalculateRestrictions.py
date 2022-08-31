import torch 
import numpy 
def calculation(pred):
    x, label = pred
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    print(f"HEREEE {c1, c2} ---- {label}")