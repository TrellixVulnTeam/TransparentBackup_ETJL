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

endZip()