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

# Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
# Copies duplicated updated files to all destinations
cp(('.', 'Deleted File.txt'), ('.', 'Lying File.txt'))
cp(('.', 'Deleted File.txt'), ('.', 'A Subdirectory', 'Deleted File.txt'))
cp(('.', 'Deleted File.txt'), ('.', 'A Subdirectory', 'Moved Lying File.txt'))
cp(('.', 'Moved and Edited File.txt'), ('.', 'A Subdirectory', 'Moved and Edited File.txt'))
cp(('.', 'Unmoved and Edited File.txt'), ('.', 'A Subdirectory', 'Unmoved and Edited File.txt'))
cp(('.', 'Unmoved and Unedited File.txt'), ('.', 'A Subdirectory', 'Unmoved & Unedited File.txt'))
