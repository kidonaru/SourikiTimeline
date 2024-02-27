import functools
import numpy as np
import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.config_utils import ProjectConfig

def get_value_str(value):
    if isinstance(value, np.ndarray):
        return "ndarray"
    elif isinstance(value, pd.DataFrame):
        return "DataFrame"
    elif TYPE_CHECKING and isinstance(value, ProjectConfig):
        return "ProjectConfig"
    else:
        return str(value)

def debug_args(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        outputs = f"{func.__name__}("
        for i, arg in enumerate(args, 1):
            outputs += f"{get_value_str(arg)}, "
        for key, value in kwargs.items():
            outputs += f"{key}': {get_value_str(value)}, "
        outputs += ")"
        print(outputs)

        return func(*args, **kwargs)

    return wrapper
