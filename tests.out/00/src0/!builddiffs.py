
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

# Copies files to be backed up to the current directory
mkdir(('.',))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Another Unmoved and Unedited File.txt'), ('.', 'Another Unmoved and Unedited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Deleted File.txt'), ('.', 'Deleted File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Moved and Edited File.txt'), ('.', 'Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Moved and Unedited File.txt'), ('.', 'Moved and Unedited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Swapped File.txt'), ('.', 'Swapped File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Unmoved and Edited File.txt'), ('.', 'Unmoved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Unmoved and Unedited File.txt'), ('.', 'Unmoved and Unedited File.txt'))
mkdir(('.', 'A Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'A Subdirectory', 'Cross-Moved and Edited File.txt'), ('.', 'A Subdirectory', 'Cross-Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'A Subdirectory', 'Cross-Moved and Unedited File.txt'), ('.', 'A Subdirectory', 'Cross-Moved and Unedited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'A Subdirectory', 'Moved and Unedited File.txt'), ('.', 'A Subdirectory', 'Moved and Unedited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'A Subdirectory', 'Swapped File.txt'), ('.', 'A Subdirectory', 'Swapped File.txt'))
mkdir(('.', 'Deleted Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Deleted Subdirectory', 'Deleted File.txt'), ('.', 'Deleted Subdirectory', 'Deleted File.txt'))
mkdir(('.', 'Moved Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Moved Subdirectory', 'Deleted File.txt'), ('.', 'Moved Subdirectory', 'Deleted File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Moved Subdirectory', 'Moved and Edited File.txt'), ('.', 'Moved Subdirectory', 'Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src0', '.', 'Moved Subdirectory', 'Moved and Unedited File.txt'), ('.', 'Moved Subdirectory', 'Moved and Unedited File.txt'))
# Diff set file count: 15
# Diff set total bytes: 1156
