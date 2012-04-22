import os
import os.path
import zipfile

def mkdir(name):
  pass

ALREADY_COMPRESSEDS = set(("zip", "tgz", "gz", "jpg", "png", "mp3", "flac", "oog", "avi", "mkv", "flv", "mov", "mp4", "m4a", "m4v"))

z = None

def startZip(p):
  global z
  z = zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED, True)

def endZip():
  z.close()

def cp(src, dst):
  mode = zipfile.ZIP_DEFLATED
  if os.path.splitext(src[-1])[1][1:].lower() in ALREADY_COMPRESSEDS:
    mode = zipfile.ZIP_STORED
  z.write(os.path.join(*src), os.path.join(*dst), mode)

startZip("diffs.zip")

# Copies files to be backed up to the current directory
mkdir((u'.',))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'Created File.txt'), (u'.', u'Created File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'Cross-Moved and Edited File.txt'), (u'.', u'Cross-Moved and Edited File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'New Moved and Edited File.txt'), (u'.', u'New Moved and Edited File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'Unmoved and Edited File.txt'), (u'.', u'Unmoved and Edited File.txt'))
mkdir((u'.', u'A Subdirectory'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'Created File.txt'), (u'.', u'A Subdirectory', u'Created File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'New Moved and Edited File.txt'), (u'.', u'A Subdirectory', u'New Moved and Edited File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'Unmoved and Edited File.txt'), (u'.', u'A Subdirectory', u'Unmoved and Edited File.txt'))
mkdir((u'.', u'Created Subdirectory'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'Created Subdirectory', u'Created File.txt'), (u'.', u'Created Subdirectory', u'Created File.txt'))
mkdir((u'.', u'New Moved Subdirectory'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'New Moved Subdirectory', u'Double Cross-Moved and Edited File.txt'), (u'.', u'New Moved Subdirectory', u'Double Cross-Moved and Edited File.txt'))
cp((u'T:\\', u'tests.in', u'00', u'src1', u'.', u'New Moved Subdirectory', u'Moved and Edited File.txt'), (u'.', u'New Moved Subdirectory', u'Moved and Edited File.txt'))
# Diff set file count: 10
# Diff set total bytes: 981

endZip()