from dataclasses import dataclass

@dataclass
class _colors:
    LOG  = '\033[94m'
    ERR  = '\033[91m'
    WARN = '\033[93m'
    DONE = '\033[0m'

def _punctuate(msg: str) -> str:
    if (not msg.endswith(".") and
        not msg.endswith("?") and
        not msg.endswith("!")):
        msg += "."
    return msg

def log(msg: str):
    msg = _punctuate(msg)
    print(f"{_colors.LOG}[LOG] {msg}{_colors.DONE}")

def warn(msg: str):
    msg = _punctuate(msg)
    print(f"{_colors.WARN}[WARN] {msg}{_colors.DONE}")

def err(msg: str):
    msg = _punctuate(msg)
    print(f"{_colors.ERR}[ERR] {msg}{_colors.DONE}")
