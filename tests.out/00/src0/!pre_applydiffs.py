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

# Prepares the previous state of the backup set, rooted in the current directory, for having the updated files copied over it
mkdir((u'.', u'A Subdirectory'))
mkdir((u'.', u'Deleted Subdirectory'))
mkdir((u'.', u'Moved Subdirectory'))
# Transfers copied files to temporary dirs
# Transfers copied files to final destination
# Clears away deleted objects and temporary dirs
