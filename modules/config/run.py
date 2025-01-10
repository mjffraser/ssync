from os         import chdir
from os.path    import exists
from subprocess import run, DEVNULL

"""""""""""""""""""""""""""""""""""""""""""""""""""
__CONFIG_VERSION__

  if changes are made to any of the following, this
  should be incremented to trigger recompilation.

  - su.py 
  - user.py 
  - shared_routine.py 
  - internal/*
"""""""""""""""""""""""""""""""""""""""""""""""""""
__CONFIG_VERSION__ = "v1.0-5"


"""""""""""""""""""""""""""""""""""""""""""""""""""
_compile
  compiles routines to do the copies.

on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _compile(py_file, r_type):
    try:
        print(f"[LOG] Compiling {r_type} routine...")
        run(["nuitka", "--onefile", "--follow-imports", f"{py_file}"], text=True, check=True, stderr=DEVNULL, stdout=DEVNULL)
        run(["rm", "-r", f"{r_type}.build", f"{r_type}.dist", f"{r_type}.onefile-build"])
        print("[LOG] done.")
    except:
        print("[ERR] An issue occured during compilation.")
        return False
    return True

"""""""""""""""""""""""""""""""""""""""""""""""""""
_elevate_perms
  chowns routinue for sudo copies to root and sets
  the setuid bit.

on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _elevate_perms(bin_file):
    try:
        print("[LOG] Changing su routine owner to root...")
        run(["sudo", "chown", "root:root", f"{bin_file}"], check=True)
        print("[LOG] done.")
        print("[LOG] Setting setuid bit...")
        run(["sudo", "chmod", "u+s", f"{bin_file}"], check=True)
        print("[LOG] done.")
    except:
        print("[ERR] An issue occured while changing binary ownership.")
        return False 
    return True

def _store_ver():
    if exists(__CONFIG_VERSION__):
        return
    
    try:
        #clear any existing version
        run(["sudo rm v*"], shell=True, check=False, text=False) #fails if no files need to be deleted

        #we generate our version file
        with open(__CONFIG_VERSION__, "w") as f:
            f.close()

        #chown to root so it's harder to mess with
        run(["sudo", "chown", "root:root", __CONFIG_VERSION__], check=True)

    except:
        print("[ERR] An issue occured creating the version file.")

def _remove_elevated_perms():
    try:
        run(["sudo", "-k"], check=True)
    except:
        print("[ERR] An issue occured removing sudo perms.")
        


"""""""""""""""""""""""""""""""""""""""""""""""""""
copy_configs
  manages the config copies that need to happen.
  handles compiling an executable to do privileged
  copies, as well as chown the file to root, and
  set the setuid bit. then invoked the executables
  it created to do the config copies and
  replacements.
  
on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def copy_configs(mode, ssync_dir, cwd, cfg_path, host_path):
    user_routine = "user.py"
    su_routine   = "su.py"

    #move to where we're compiling stuff
    chdir(ssync_dir + "/modules/config/routines/")

    if exists(__CONFIG_VERSION__):
        print("[LOG] Nothing to compile. Skipping...")
    else:
        if not _compile(user_routine, "user"):
            return False
        if not _compile(su_routine, "su"):
            return False
        if not _elevate_perms("su.bin"):
            return False
        _store_ver()
        _remove_elevated_perms()

    #mode was verified by sync.py
    run(["./user.bin", str(mode), cfg_path, host_path])
    run(["./su.bin",   str(mode), cfg_path, host_path])
    
    #exit out
    chdir(cwd)
    return True
