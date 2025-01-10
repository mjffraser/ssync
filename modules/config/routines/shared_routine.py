from internal.parsing          import CopyData, read_config
from internal.copy_and_replace import copy_configs

from sys import argv

def shared_main(su: bool):
    #so long as this is called by run.py, it should pass the args correctly every time
    #if this errors it's fine because the program will error anyway without the mode
    args = argv

    mode = -1
    if    args[1] == "0": mode = 0
    elif  args[1] == "1": mode = 1
    else: return -1 

    cfg_path  = args[2]
    host_path = args[3]

    copies, spec_replacements = read_config(su, cfg_path) 
    copy_data = CopyData(mode, su, copies, spec_replacements, host_path)
    ret = copy_configs(mode, copy_data.host_data, copy_data.copies) 
    if not ret:
      return -1 
