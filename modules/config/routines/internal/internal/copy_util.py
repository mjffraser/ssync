from os.path import exists, isdir, dirname
from os      import makedirs
from shutil  import copytree, copy2

"""""""""""""""""""""""""""""""""""""""""""""""""""
copy:
  function to do either a backup or deployment
  copy. always returns, even on error, and prints
  a message to console if something happened so the
  user can address it how they see fit.

always returns.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def copy(src, dest):
    if not exists(src): 
        print(f"[LOG] Source \'{src}\' appears to not exist!")
        return

    
    if not exists( dirname(dest) ):
        makedirs(dest) 


    

    #do copy
    try:
        if isdir(src):
            #copy all files in directory
            copytree(src, dest, dirs_exist_ok=True)
        else:
            print(f"{src}    {dest}")
            #copy file
            copy2(src, dest)
    except Exception as e: #most likely shutil.Error, but we want to catch any issue to help diagnose
        print(f"[ERR] An error occured copying from \'{src}\' to \'{dest}\'")
        print(e)
