import yaml, os, subprocess, codecs
from typing import List, Tuple

from log_tools import warn, err, log

def _split_bltosl(packages: bytes) -> List[str]:
    pkg_list = packages.splitlines() 
    return [x.decode('UTF-8') for x in pkg_list]

def _normal_packages() -> List[str]:
    packages = subprocess.check_output(["pacman", "-Qqen"])
    return _split_bltosl(packages)

def _foreign_packages() -> List[str]:
    packages = subprocess.check_output(["pacman", "-Qqem"])
    return _split_bltosl(packages)

#keys to index data in config yaml
_normal_key = "normal-pkgs"
_aur_key    = "aur-pkgs"
_host_key   = "host-spec-pkgs"

#prefixes for host packages
_normal_prefix = "|n|"
_aur_prefix    = "|a|"

def setup_sync(mode:           int,
               config_path:    str,
               host_data_path: str) -> Tuple[List[str], List[str], List[str]]:

    #pull normal and aur packages from either system for backup, or config for deploy
    normal = []
    aur    = []
    config_data = None
    if mode == 1:
        try:
            with open(config_path, "r") as file:
                config_data = yaml.safe_load(file)
            normal = config_data.get(_normal_key, [])
            aur    = config_data.get(_aur_key,    [])
        except:
            err(f"An issue occured reading config data at {config_path}")
            err("This is critical to deployment, cannot proceed.")
    else:
        normal = _normal_packages()
        aur    = _foreign_packages()

    #if we're deploying and read 0 packages
    if config_data is None and mode == 1:
        return ([],[],[])

    #read in host data, if it exists
    host_data = None
    try:
        with open(host_data_path, "r") as file:
            host_data = yaml.safe_load(file)
    except:
        warn(f"An issue occured reading host_data at {host_data_path}")
        warn("If there are machine specific packages they won't be properly synced/removed from the backup up list.")

    if host_data is None:
        host_data     = {}
    
    host_packages = host_data.get(_host_key, [])
    if not host_packages:
        log("No host-spec packages detected.")
    else:
        log("Dropping packages:")
        buff = ""
        for pkg in host_packages:
            if pkg.startswith(_normal_prefix):
                name = pkg.removeprefix(_normal_prefix)
            elif pkg.startswith(_aur_prefix):
                name = pkg.removeprefix(_aur_prefix)
            else:
                continue

            if (len(buff) + len(name)) >= 80:
                log(buff)
                buff = ""
            buff += name + " " 
        if len(buff) > 0:
            log(buff)


    return (normal, aur, host_packages)

def do_sync(mode:        int,
            config_path: str,
            packages:    Tuple[List[str], List[str], List[str]]):
    normal_pkg, aur_pkg, host_pkg = packages
    if len(normal_pkg) < 1 and len(aur_pkg) < 1:
        log("Nothing to do...")
        return #nothing to do


    #split the host package list
    host_norm     = []
    host_aur      = []
    for pkg in host_pkg:
        if pkg.startswith(_normal_prefix):
            host_norm.append(pkg.removeprefix(_normal_prefix))
        elif pkg.startswith(_aur_prefix):
            host_aur.append(pkg.removeprefix(_aur_prefix))

    #backup
    if mode == 0:
        backup_normal = [pkg for pkg in normal_pkg if pkg not in host_norm]
        backup_aur    = [pkg for pkg in aur_pkg    if pkg not in host_aur ]

        data                = {}
        data["normal-pkgs"] = backup_normal
        data["aur-pkgs"]    = backup_aur
        with open(config_path, "w") as file:
            file.write(yaml.dump(data))

    #deploy
    else:
        normal_pkg_str = ' '.join(normal_pkg)
        aur_pkg_str    = ' '.join(aur_pkg)

        res = input("\033[94mSkip -Syu? [y/N]\033[0m").lower() 
        if res != 'y':
            subprocess.run(["sudo", "pacman", "-Syu"])

        log("Installing normal packages:")
        subprocess.run(["sudo", "pacman", "-S", "--needed", normal_pkg_str])
        log("Installing foreign packages:")
        subprocess.run(["yay", "-S", "--needed", aur_pkg_str])

    log("done.")
