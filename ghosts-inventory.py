#!/usr/bin/python

ghosts = '/usr/bin/ghosts'           # ghosts command
ghosts_file = '/etc/ghosts'          # ghosts database
ansible_cache = '/etc/ansible/.hosts.json'  # inventory cache
ansible_hash = '/etc/ansible/.hosts.hash'   # hash of ghosts_file


import argparse, hashlib
import os, sys, json

def lu_die(msg, exitcode=123):
  print "ERROR: ", msg
  sys.exit(exitcode)

def lu_debug(msg):
  if 'LU_DEBUG' in os.environ and os.environ['LU_DEBUG'] == "1":
    print >> sys.stderr, "[DEBUG] " + msg

def get_args():
  parser = argparse.ArgumentParser(description='Process args for retrieving Ghost servers')
  group = parser.add_mutually_exclusive_group()
  group.add_argument('--list',
                       required=False, action='store_true',
                       help='all hosts')
  group.add_argument('--gencache',
                       required=False, action='store_true',
                       help='generate cache file')
  group.add_argument('--host',
                       required=False, action='store', type=str,
                       nargs=1, help='select specific server')
  args = parser.parse_args()
  return args

def getHostVars(host):
  # return variables for selected host
  # we currently dont have any variables configured through gsh,
  # so always return empty hash
  cmd = ghosts + ' ' + host
  s = os.popen(cmd).read().rstrip().split(' ')
  if len(s) != 1:
    lu_die("Wrong number of servers returned by '" + cmd + "': " + ' '.join(s))
  elif s[0] == '':
    lu_die("Command '" + cmd + "' returned no servers")
  else:
    inventory = {}
    dumpJson(inventory)

def addHostToGroup(group, host):
  host_group = inventory.get(group, {})
  hosts = host_group.get('hosts', [])
  hosts.append(host)
  host_group['hosts'] = hosts
  inventory[group] = host_group

def calcInventory():
  # TODO: ugly, please do this in Python instead
  group = os.popen('for i in $(seq 3 9); do awk \'!/^#/ {if (NF >= \'"$i"\') print \'"\$$i"\'}\' /etc/ghosts ; done | sort -u | grep -v \-').read().strip().split('\n')
  for g in group:
    hosts = os.popen(ghosts + ' ' + g).read().rstrip().split(' ')
    for h in hosts:
      addHostToGroup(g, h)

def dumpJson(j):
  print(json.dumps(j, indent=4))

def getHash(file):
  return hashlib.md5(open(file, 'r').read()).hexdigest()

# decide if cache should be (re)written
# Return: bool
def isCacheOld():
  lu_debug("inside isCacheOld")
  ghosts_hash = getHash(ghosts_file)
  if os.path.isfile(ansible_cache) and os.path.isfile(ansible_hash):
    f = open(ansible_hash, 'r')
    h = f.readline().rstrip()
    f.close()
    if ghosts_hash == h:
      # no need to re-write ansible_cache
      lu_debug("ghosts_hash == h")
      return False
    else:
      # cache is old/dirty
      lu_debug("ghosts_hash != h")
      return True
  else:
    # if ansible_cache or ansible_hash are not found
    return True

def genCache():
  ghosts_hash = getHash(ghosts_file)
  with open(ansible_cache, 'w') as f:    
        json.dump(inventory, f)
  f.close()
  f = open(ansible_hash, 'w')
  f.write(ghosts_hash + '\n')
  f.close()

def readCache():
  with open(ansible_cache) as f:    
    inventory = json.load(f)

# main
inventory = {}
inventory['_meta'] = { 'hostvars': {} }
args = get_args()
if args.list:
  lu_debug("inside args.list")
  if isCacheOld():
    lu_debug("before calc")
    calcInventory()
  else:
    lu_debug("before read")
    with open(ansible_cache) as f:    
      inventory = json.load(f)
  lu_debug("before dumpJson")
  dumpJson(inventory)
elif args.host:
  getHostVars(args.host[0])
elif args.gencache:
  calcInventory()
  genCache()
else:
  # replace lu_die with help text
  lu_die("Unknown state detected. Bail...")
