import os, subprocess

from log_tools import log, err

"""""""""""""""""""""""""""""""""""""""""""""""""""
nuitka_compile
  compiles a .py module with nuitka where the final
  binary is: name.bin

on success:
  returns True
on failure:
  returns False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def nuitka_compile(main_py: str, name: str) -> bool:
    try:
        log(f"Compiling {name} routine...")
        subprocess.run(["nuitka", "--onefile", "--follow-imports", f"{main_py}"], text=True, check=True)
        subprocess.run(["rm", "-r", f"{name}.build", f"{name}.dist", f"{name}.onefile-build"])
        log("done")
    except:
        err("An issue occured while compiling.")
        return False
    return True

"""""""""""""""""""""""""""""""""""""""""""""""""""
chown_root
  chowns the provided file to root.

on success:
  returns True
on failure:
  return False
"""""""""""""""""""""""""""""""""""""""""""""""""""
def chown_root(file: str) -> bool:
    try:
        log("Changing routine owner to root...")
        subprocess.run(["sudo", "chown", "root:root", f"{file}"], check=True)
        log("done")
    except:
        err(f"An error occured while chaning ownership of {file}")
        return False
    return True

def setuid(file: str) -> bool:
    try:
        log("Setting setuid bit...")
        subprocess.run(["sudo", "chmod", "u+s", f"{file}"], check=True)
        log("done")
    except:
        err(f"An error occured while setting setuid for {file}")
        return False
    return True

def drop_perms() -> bool:
    try:
        subprocess.run(["sudo", "-k"], check=True)
    except:
        err("An issue occured clearing cached sudo perms.")
        return False
    return True

def store_ver(ver: str) -> bool:
    if os.path.exists(ver):
        return True
    try:
        #no check as this can fail if no version files exist
        subprocess.run(["sudo rm v*"], shell=True, check=False, text=False)
        with open(ver, "w") as file:
            file.close()
        chown_root(ver)
    except:
        err("An error occured creating the version file.")
        return False
    return True
