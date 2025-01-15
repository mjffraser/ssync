import shutil, os

#log tools is inserted into os.path before this comes into scope
from log_tools import log, err

"""""""""""""""""""""""""""""""""""""""""""""""""""
copy:
  function to do either a backup or deployment
  copy. always returns, even on error, and prints
  a message to console if something happened so the
  user can address it how they see fit.

always returns.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def copy(src, dest):
    if not os.path.exists(src): 
        err(f"Source \'{src}\' appears to not exist!")
        return

    if not os.path.exists( os.path.dirname(dest) ):
        os.makedirs( os.path.dirname(dest) ) 

    #do copy
    try:
        if os.path.isdir(src):
            #copy all files in directory
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            #copy file
            shutil.copyfile(src, dest)

    except Exception as e: #most likely shutil.Error, but we want to catch any issue to help diagnose
        err(f"An error occured copying from \'{src}\' to \'{dest}\'")
        err(str(e))
