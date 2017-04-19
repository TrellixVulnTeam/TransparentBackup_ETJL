import sys
import os
import os.path
import shutil

FS_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

def mkdir (name):
  p = os.path.join(*name)
  if not os.path.isdir(p):
    os.makedirs(p)

def rmdir (name):
  os.rmdir(os.path.join(*name))

def cp (src, dst):
  s = os.path.join(*src)
  d = os.path.join(*dst)
  if os.path.islink(s):
    os.symlink(os.readlink(s.encode(FS_ENCODING)), d)
  else:
    shutil.copy2(s, d)

def mv (src, dst):
  s = os.path.join(*src)
  d = os.path.join(*dst)
  if os.path.islink(s):
    os.symlink(os.readlink(s.encode(FS_ENCODING)), d)
    os.remove(s)
  else:
    shutil.move(s, d)

def rm (name):
  os.remove(os.path.join(*name))

# Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
# Copies duplicated updated files to all destinations
cp((u'.', u'Created File.txt'), (u'.', u'New Moved Subdirectory', u'Created File.txt'))
