"""Shared safety checks of the Token Diet tools: never print more than the input, cap the input size.

Not a command: imported by compactar.py, resumir.py and convertir_fuentes.py.
"""
import math
import pathlib

MAX_INPUT_BYTES = 64 * 1024 * 1024
NOT_WORTH = "not worth compacting: the result is not meaningfully smaller than the original, read the original"


def tokens(text):
    return math.ceil(len(text) / 4)


MIN_GAIN = 0.05


def worth(before, after, min_gain=MIN_GAIN):
    """True only when `after` tokens are at least `min_gain` below `before` (a one-token gain is noise)."""
    return after < before and after <= before * (1 - min_gain)


def never_worse(original, result):
    """True only when the result is meaningfully smaller than the original, in tokens."""
    return worth(tokens(original), tokens(result))


def check_size(path, cap=None):
    """Raises ValueError for an input above the cap, with the way out."""
    limit = MAX_INPUT_BYTES if cap is None else cap
    size = pathlib.Path(path).stat().st_size
    if size > limit:
        raise ValueError(f"{pathlib.Path(path).name} is {size / 2**20:.0f} MiB, above the {limit / 2**20:.0f} MiB cap: read it by line ranges")
