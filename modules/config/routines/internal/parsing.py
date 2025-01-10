from os.path     import expandvars, expanduser, join, exists
from dataclasses import dataclass, field
from yaml        import safe_load, dump
from typing      import List, Tuple

"""""""""""""""""""""""""""""""""""""""""""""""""""
CopySpec:
  small object to house copy information. 
  file_specs is a list of all validated specific
  file copies. they're in the form:
    [ rel_f_path, repl_key, repl_kv, host_key ]
  where:
  
  repl_f_path: additional local file path to add to
               the `to_path`, where this file is 
               opened and modified post-copy.

  repl_key:    the pattern to search for in each
               line. if it's matched the line is
               replaced.

  repl_kv:     the value to either be swapped out 
               for the key in backup mode, or is 
               used to replace the key in deploy 
               mode.

  host_key:    the key used to index the machine-
               specific data for a replacement. if
               in backup mode, this key will be
               used to store the value, and if in
               deploy mode, this key is used to
               retrieve this value. 
"""""""""""""""""""""""""""""""""""""""""""""""""""
@dataclass
class CopySpec:
    to_path:    str #path to file or directory
    from_path:  str #path to file or directory
    file_specs: List[Tuple[str,str,str,str]] = field(default_factory=list) 


#whitelisted copies to files owned by root.
#these operations are performed by root so this protects against rouge operations in the config
_authorized_sudo_copies = [
    "/etc/greetd/config.toml"
]

"""""""""""""""""""""""""""""""""""""""""""""""""""
_check_specifics:
  function to validate copies, and the specific 
  value copies for specific files.

on success:
  returns CopySpec.
on failure:
  returns None.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def _check_specifics(mode, sys_path, links_path, spec_file_repl, spec_repl_dict, host_data, unexpanded_path):
    if host_data is None and mode == 1 and len(spec_file_repl) > 0:
        print(f"[ERR] No host data stored! Ending search for {spec_file_repl}")
        return None

    #check path types
    if not isinstance(sys_path, str) or not isinstance(links_path, str):
        return None

    #verify something exists to copy
    if mode == 1: #deploy
        if not exists(links_path):
            print(f"[ERR] Path: {links_path} appears to not exist?")
            return None 
    else: #backup
        if not exists(sys_path):
            print(f"[ERR] Path: {sys_path} appears to not exist?")
            return None

    #now we setup the copies that need to happen
    copies = CopySpec("", "")

    #first we validate the copy from sys_path to links_path or vice versa
    if mode == 1: #deploy mode
        copies.to_path   = sys_path
        copies.from_path = links_path
    else: #backup mode
        copies.to_path   = links_path
        copies.from_path = sys_path


    #if we have specfic file edits to do, we add those
    if len(spec_file_repl) > 0:
        for file in spec_file_repl:
            if not isinstance(file, str):
                print(f"[WARN] {file} appears to not be a string?")
                continue
            
            #this is not a directory copy, but a single file, so target that file
            if file == ".":
                spec_key = unexpanded_path #we use this to look up the replacements to do
                if mode == 1:
                    repl_f_path = sys_path
                else:
                    repl_f_path = links_path 

            #directory copy, so build the path to the file
            else:
                spec_key = join(unexpanded_path, file)
                if mode == 1:
                    repl_f_path = join(sys_path, file)
                else:
                    repl_f_path = join(links_path, file)

            #get what $HOME is equivalent to
            print(spec_key)

            specifics = spec_repl_dict.get(spec_key, None)

            #check an entry exists for it in specific_replacements
            if specifics is not None:
                for replacement in specifics:
                    #we have file path already in file_name
                    if len(replacement) != 2:
                        print(f"[WARN] {replacement} does not contain key/val pair? Len:{len(replacement)}")
                        continue 
                    
                    repl_key = replacement[0]
                    repl_kv  = replacement[1] + "\n"
                    host_key = spec_key + "-" + repl_key

                    #if we're in deploy mode, we need to check that data exists for the specific replacement
                    if mode == 1:
                        data = host_data.get(host_key, None)
                        if data is None:
                            print(f"[WARN] {replacement} does not have a host-specific value stored already." 
                                   "Performing a backup can help auto-generate the entry.")
                            continue 
                     
                    copies.file_specs.append( (repl_f_path, repl_key, repl_kv, host_key) )

    return copies

"""""""""""""""""""""""""""""""""""""""""""""""""""
read_config
  function that reads the config.yaml file for
  either user or su copies, returning the copy
  instructions and the specific_replacements to
  match.

returns:
  [copies to do, replacements for those copies]
"""""""""""""""""""""""""""""""""""""""""""""""""""
def read_config(su: bool, cfg_path):
    #open config file
    with open(cfg_path, "r") as file:
        data = safe_load(file)

    #read copies from config
    if "config" not in data:
       raise KeyError("No config section exists in config.yaml?") 

    if su:
        copies = data["config"].get("sudo_copies", [])
    else:
        copies = data["config"].get("user_copies", [])

    #if specific replacements should be done on some of those copies, check for and import these too
    specific_replacements = {}
    if "specific_replacements" in data:
        specific_replacements = data.get("specific_replacements", {})

    return copies, specific_replacements

"""""""""""""""""""""""""""""""""""""""""""""""""""
CopyData:
  object that parses any copy and replacement
  operations that need to happen. 
"""""""""""""""""""""""""""""""""""""""""""""""""""
class CopyData:
    mode        = 0
    su          = False 
    copies      = [] #validated copies
    host_data   = None
    host_path   = ""

    def __init__(self, mode, su, copies, specific_replacements_dict, host_path):
        self.mode      = mode
        self.su        = su
        self.host_path = host_path 

        if exists(host_path):
            with open(host_path, "r") as file:
                self.host_data = safe_load(file)
     
        if self.host_data is None:
            self.host_data = {}

        #import copies & replacements
        for sys_path, links_path, specific_file_replacements in copies:
            if not isinstance(sys_path, str):
                print(f"[ERR] {sys_path} is not a valid string.")
                continue
            if not isinstance(links_path, str):
                print(f"[ERR] {links_path} is not a valid string.")
                continue 
            if not isinstance(specific_file_replacements, list):
                print(f"[ERR] {specific_file_replacements} is not a valid list of strings. An empty list is required for no spec. copies.")
                continue

            expanded_sys   = expandvars(sys_path)
            expanded_links = expandvars(links_path)

            if sys_path not in _authorized_sudo_copies and self.su:
                continue
            copy_spec = _check_specifics(self.mode, 
                                         expanded_sys, 
                                         expanded_links, 
                                         specific_file_replacements, 
                                         specific_replacements_dict, 
                                         self.host_data,
                                         links_path)
            self.copies.append(copy_spec)

    def __del__(self):
        if isinstance(self.host_data, (dict, list)):
            with open(self.host_path, "w") as file:
                file.write(dump(self.host_data))

