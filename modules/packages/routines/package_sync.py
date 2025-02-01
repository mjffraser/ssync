import os, sys

def sync_pkgs():
    #now that we've brought log_tools into environment
    from log_tools import log, err
    log("Doing package sync...")

    #read args from driver program
    args = sys.argv
    mode = -1
    if args[1]   == "0": mode = 0
    elif args[1] == "1": mode = 1
    else: 
        err("Backup/Deploy mode not set!")
        return -1 
    cfg_path = args[2]
    host_path = args[3]

    #now we have everything to do the sync
    #we import here now so we can do a single import of log tools for all functions
    from internal.parsing import setup_sync, do_sync 
    packages = setup_sync(mode, cfg_path, host_path)

    #TODO: determine list outliers and ask verification
    #FOR NOW: proceed with no checks

    do_sync(mode, cfg_path, packages)

if __name__ == "__main__":
    sys.path.append(os.environ["PYTHONPATH"])
    sync_pkgs()

