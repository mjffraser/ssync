from shared_routine import shared_main

import sys
import os

if __name__ == "__main__":
    sys.path.append(os.environ["PYTHONPATH"]) 
    from log_tools import log
    log("Doing user copies...")
    shared_main(False)
