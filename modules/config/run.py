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
__CONFIG_VERSION__ = "v1.2-2"

"""""""""""""""""""""""""""""""""""""""""""""""""""
copy_configs
  manages the config copies that need to happen.
  handles compiling an executable to do privileged
  copies, as well as chown the su routine file to 
  root, and set the setuid bit. then invokes the 
  executables it created to do the config copies
  and replacements.
  
on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def copy_configs(mode, 
                 ssync_dir, 
                 cwd, 
                 cfg_path, 
                 host_path, 
                 default_path,
                 global_module_path):
    user_routine = "user.py"
    su_routine   = "su.py"

    #move to where we're compiling stuff
    os.chdir(ssync_dir + "/modules/config/routines/")

    if (os.path.exists(__CONFIG_VERSION__) and not 
        __CONFIG_VERSION__.endswith("-0")):
        log("Nothing to compile. Skipping...")
    else:
        if not all((
            run_util.nuitka_compile(user_routine, "user"),
            run_util.nuitka_compile(su_routine,   "su"),
            run_util.chown_root("su.bin"),
            run_util.setuid("su.bin"),
            run_util.store_ver(__CONFIG_VERSION__),
            run_util.drop_perms()
        )):
            return False

    os.environ["PYTHONPATH"] = global_module_path
    subprocess.run(["./user.bin", str(mode), cfg_path, host_path, default_path], env=os.environ)
    subprocess.run(["./su.bin",   str(mode), cfg_path, host_path, default_path], env=os.environ)
    
    #exit out
    os.chdir(cwd)
    return True
