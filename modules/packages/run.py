import os, subprocess

#log tools is inserted into path before this comes into scope
from log_tools import log 
from ..        import run_util

"""""""""""""""""""""""""""""""""""""""""""""""""""
__CONFIG_VERSION__

  if changes are made to any of the following, this
  should be incremented to trigger recompilation.

  - su.py 
  - user.py 
  - shared_routine.py 
  - internal/*
"""""""""""""""""""""""""""""""""""""""""""""""""""
__CONFIG_VERSION__ = "v1.0-7"


"""""""""""""""""""""""""""""""""""""""""""""""""""
sync_packages
  manages packages installed via pacman & yay.

on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def sync_packages(mode,
                  ssync_dir,
                  cwd,
                  cfg_path,
                  host_path,
                  global_module_path):
    routine = "package_sync.py"

    #cd into packages/routines/
    os.chdir(ssync_dir + "/modules/packages/routines/")

    if (os.path.exists(__CONFIG_VERSION__) and not __CONFIG_VERSION__.endswith("-0")):
        log("Nothing to compile. Skipping...")
    else:
        if not all((
            run_util.nuitka_compile(routine, "package_sync"),
            run_util.store_ver(__CONFIG_VERSION__),
            run_util.drop_perms()
        )):
            return False

    os.environ["PYTHONPATH"] = global_module_path
    subprocess.run(["./package_sync.bin", str(mode), cfg_path, host_path], env=os.environ)
    
    #exit out
    os.chdir(cwd)
    return True



