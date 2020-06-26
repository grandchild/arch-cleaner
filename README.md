## arch-cleaner
Interactively uninstall arch packages that you forgot you ever had installed.

### Description
This script goes through all explicitly installed packages. For each package it will ask you to show the description and/or if you want to uninstall it.

### Usage
Have a look at the flags, since the default behaviour might not do all you want, and might not be most convenient for you.

```
usage: ./arch-cleaner.py [-h] [-c] [-d] [--core] [--version]

-h, --help            show this help message and exit
-c, --collect         don't delete right away, store and delete on SIGTERM or finish.
-d, --show-desc       don't ask to show description, show it right away.
-n, --remove-configs  remove configuration and other normally backupped files.
--core                suggest packages from core repository as well.
--version             show program's version number and exit
```

### License
[<img src='https://img.shields.io/badge/license-CC0-blue.svg'/>](https://creativecommons.org/publicdomain/zero/1.0)
