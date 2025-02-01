import os, sys, yaml

from env_pkg.log_tools  import warn, err

"""""""""""""""""""""""""""""""""""""""""""""""""""
mode (required)
  0  -> backup mode
  1  -> deploy mode
  -1 -> none selected (default)

sync_configs (optional)
  true  -> execute config module
  false -> (default)

sync_packages (optional)
  true  -> execute packages module
  false -> (default)
"""""""""""""""""""""""""""""""""""""""""""""""""""
_mode                   = -1
_sync_configs           = False
_sync_packages          = False

"""""""""""""""""""""""""""""""""""""""""""""""""""
_usage_err
  prints a usage message for the user and exits
  out. designed to be called on a critical error in
  command line args.

always exits.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _usage_err():
    print("[backup]   -> -b or --backup; copies files from disk to target destination for backup.")
    print("[deploy]   -> -d or --deploy; copies files from target destination to disk to update system configs.")
    print("[config]   -> -c or --copy-configs; if the config module should be executed. See README for details.")
    print("[packages] -> -p or --copy-packages; if the packages module should be exected. See README for details.")
    print("EXAMPLE USAGE: python ssync -bcp")
    exit()


"""""""""""""""""""""""""""""""""""""""""""""""""""
_parse_option
  parses a command line arg in the form -[...]
  where [...] are one or more of:

  b -> backup mode   (sets mode to 0)
  d -> deploy mode   (sets mode to 1)
  c -> copy configs  (sets sync_configs to true)
  p -> copy packages (sets sync_packages to true) 
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _parse_option(arg: str):
    if len(arg) < 2:
        warn(f"No options supplied after the '-'")
        return

    global _mode, _sync_configs, _sync_packages
    for c in arg:
        if c   == "-": pass
        elif c == "b": _mode          += 1
        elif c == "d": _mode          += 2
        elif c == "c": _sync_configs   = True
        elif c == "p": _sync_packages  = True
        else: warn(f"Option {c} not recognized.")

"""""""""""""""""""""""""""""""""""""""""""""""""""
_parse_args
  parses all args provided, calling _parse_option
  as needed.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _parse_args():
    global _mode, _sync_configs, _sync_packages
    args = sys.argv 
    if len(args) < 2:
        err("No copy mode specified!")
        _usage_err()
   
    #process args until we error for any reason (no arg, problematic arg)
    i = 0
    while True:
        i += 1 
        try:
            arg_str = str(args[i])
            if arg_str.startswith("--"):
                if   arg_str == "--backup":        _mode          += 1
                elif arg_str == "--deploy":        _mode          += 2
                elif arg_str == "--copy-configs":  _sync_configs   = True
                elif arg_str == "--copy-packages": _sync_packages  = True
                else: _usage_err()
            elif arg_str.startswith("-"):
                _parse_option(arg_str)
            else: 
                warn(f"Argument {arg_str} not recognized.") 
        except: 
            #catches err when we do args[i] with too large an i
            #therefore no more args to process
            break  

def main():
    _parse_args() 
    if _mode < 0:
        err("No valid mode provided.")
        _usage_err()

    if _mode > 1:
        err("Both deploy and backup mode selected.")
        _usage_err()

    cwd       = os.path.abspath(os.getcwd())
    ssync_dir = os.path.dirname(os.path.abspath(__file__))

    #add global logging functions to path temporarily so all other modules can find them
    global_path_dir = ssync_dir + "/env_pkg/"
    sys.path.append(global_path_dir)

    #now import with updated path
    from modules.config.run   import copy_configs
    from modules.packages.run import sync_packages

    ssync_cfg = ssync_dir + "/config.yaml"
    with open(ssync_cfg, "r") as cfg:
        config = yaml.safe_load(cfg) 

    copy_config  = ""
    pkg_config   = ""
    host_path    = os.path.expandvars(config.get("host-data-path",    "$HOME/.config/ssync-host-data.yaml"))
    default_path = os.path.expandvars(config.get("default-host-data", ""                                  ))

    #checks before we execute any modules
    dirty = 0
    if _sync_configs:
        copy_config   = os.path.expandvars(config.get("copy-config-path", "$HOME/.config/ssync-copy-config.yaml"))
        if not os.path.exists(copy_config):
            warn(f"Copy-configs config file at supplied path {copy_config} appears to not exist?")
            dirty += 1
        if not os.path.isfile(copy_config):
            warn(f"Copy-configs config file at supplied path {copy_config} appears to not be a file?")
            dirty += 1

    if _sync_packages:
        pkg_config = os.path.expandvars(config.get("copy-package-path", "$HOME/.config/ssync-pkg-config.yaml"))
        if not os.path.exists(pkg_config):
            warn(f"Copy-packages config file at supplied path {pkg_config} appears to not exist?")
            dirty += 1
        if not os.path.isfile(pkg_config):
            warn(f"Copy-packages config file at supplied path {pkg_config} appears to not be a file?")
            dirty += 1

    
    if dirty > 0:
        err("Critical configs are missing. Cannot proceed.")
        exit()

    #config module
    if _sync_configs:
        copy_configs(_mode, 
                     ssync_dir, 
                     cwd, 
                     copy_config, 
                     host_path, 
                     default_path,
                     global_path_dir)

    #packages module
    if _sync_packages:
        sync_packages(_mode, 
                      ssync_dir, 
                      cwd, 
                      pkg_config, 
                      host_path,
                      global_path_dir)

if __name__ == "__main__":
    main();
