"""""""""""""""""""""""""""""""""""""""""""""""""""
replace:
  function to do specific replacements for files.
  if any error occurs in the process, an error
  message is printed, and the function exits
  safely.

backup:
  searches file at rel_f_path to find repl_key and
  replaces that line with repl_kv. uses host_key
  to record the machine-specific line into
  host_data.yaml.

deploy:
  searchs file at rel_f_path to find repl_kv and
  replaces that line with the value inside 
  host_data, accessed via host_key.

always returns.
"""""""""""""""""""""""""""""""""""""""""""""""""""
def replace(mode:       int,
            rel_f_path: str,
            repl_key:   str,
            repl_kv:    str,
            host_key:   str,
            host_data): #dictionary representing host_data yaml
    try: 
        with open(rel_f_path, "r") as file:
            lines = file.readlines() 
    except Exception as e:
        print(f"[ERR] An error occured opening and reading from \'{rel_f_path}\'. Is is readable?")
        print(e)
        return 
 
    for i in range(len(lines)):
        if mode == 1:
            if repl_kv in lines[i]:
                lines[i] = host_data[host_key]
        else: #backup
            if repl_key in lines[i]:
                host_data[host_key] = lines[i]
                lines[i] = repl_kv 

    try:
        with open(rel_f_path, "w") as file:
            file.writelines(lines)
    except Exception as e:
        print(f"[ERR] An error occured opening and writing back to \'{rel_f_path}\'. Is it writable?")
        print(e)
        return
