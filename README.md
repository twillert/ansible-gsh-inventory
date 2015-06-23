# Ansible Inventory script for GSH (ghosts)
This is an Ansible inventory script for GSH (ghosts / https://github.com/kees/gsh)

# Requirements
GSH - https://github.com/kees/gsh

# Usage
You can use like this:

```
$ ansible <server/group> -i ghosts-inventory.py -m ping
```

Or set it statically in your ansible.cfg:

```
[defaults]
inventory = /opt/lunar/scripts/ghosts-inventory.py
```

Do not forget that Ansible with its "patterns" princicple has builtin GSH-like behaviour when it comes to server grouping/selection (http://docs.ansible.com/intro_patterns.html)

