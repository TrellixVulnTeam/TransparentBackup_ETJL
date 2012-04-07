
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
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'Created File.txt'), ('.', 'Created File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'Cross-Moved and Edited File.txt'), ('.', 'Cross-Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'New Moved and Edited File.txt'), ('.', 'New Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'Unmoved and Edited File.txt'), ('.', 'Unmoved and Edited File.txt'))
mkdir(('.', 'A Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'A Subdirectory', 'Created File.txt'), ('.', 'A Subdirectory', 'Created File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'A Subdirectory', 'New Moved and Edited File.txt'), ('.', 'A Subdirectory', 'New Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'A Subdirectory', 'Unmoved and Edited File.txt'), ('.', 'A Subdirectory', 'Unmoved and Edited File.txt'))
mkdir(('.', 'Created Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'Created Subdirectory', 'Created File.txt'), ('.', 'Created Subdirectory', 'Created File.txt'))
mkdir(('.', 'New Moved Subdirectory'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'New Moved Subdirectory', 'Double Cross-Moved and Edited File.txt'), ('.', 'New Moved Subdirectory', 'Double Cross-Moved and Edited File.txt'))
cp(('T:\\', 'tests.in', '00', 'src1', '.', 'New Moved Subdirectory', 'Moved and Edited File.txt'), ('.', 'New Moved Subdirectory', 'Moved and Edited File.txt'))
# Diff set file count: 10
# Diff set total bytes: 981
