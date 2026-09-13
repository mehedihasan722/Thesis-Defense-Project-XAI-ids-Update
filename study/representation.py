"""Common finite numeric representation used before model-specific scaling."""
import numpy as np

def log_values(x):
    x=np.asarray(x,dtype=np.float64)
    if not np.isfinite(x).all():raise ValueError('Non-finite raw features must be cleaned before encoding')
    # Float32 is the common tree-library input precision. Hash this exact
    # representation too, so rounding-equivalent flows remain in one split.
    return (np.sign(x)*np.log1p(np.abs(x))).astype(np.float32).astype(np.float64)
