import os
import os.path
import zipfile

def mkdir(name):
  pass

z = None

def startZip(p):
  global z
  z = zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED, True)

def endZip():
  z.close()

def cp(src, dst):
  z.write(os.path.join(*src), os.path.join(*dst))

startZip("diffs.zip")

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

endZip()