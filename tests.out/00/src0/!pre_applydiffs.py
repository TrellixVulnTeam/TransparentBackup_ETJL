import os
import os.path
import shutil

def mkdir(name):
  p = os.path.join(*name)
  if not os.path.isdir(p):
    os.makedirs(p)

def rmdir(name):
  os.rmdir(os.path.join(*name))

def cp(src, dst):
  shutil.copy2(os.path.join(*src), os.path.join(*dst))

def mv(src, dst):
  shutil.move(os.path.join(*src), os.path.join(*dst))

def rm(name):
  os.remove(os.path.join(*name))

# Prepares the previous state of the backup set, rooted in the current directory, for having the updated files copied over it
mkdir(('.', 'A Subdirectory'))
mkdir(('.', 'Deleted Subdirectory'))
mkdir(('.', 'Moved Subdirectory'))
# Transfers copied files to temporary dirs
# Transfers copied files to final destination
# Clears away deleted objects and temporary dirs
