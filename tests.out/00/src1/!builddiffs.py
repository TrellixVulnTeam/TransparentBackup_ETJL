import sys
import os
import os.path
import zipfile
import time

def mkdir (name):
  pass

FS_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

ALREADY_COMPRESSEDS = set(("zip", "tgz", "gz", "jpg", "png", "mp3", "flac", "oog", "avi", "mkv", "flv", "mov", "mp4", "m4a", "m4v"))

z = None

def startZip (p):
  global z
  z = zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED, True)

def endZip ():
  z.close()

def cp (src, dst):
  s = os.path.join(*src)
  if os.path.islink(s):
    st = os.lstat(s)
    # (see http://www.mail-archive.com/python-list@python.org/msg34223.html and zipfile.ZipFile.write())
    info = zipfile.ZipInfo("/".join(p for p in dst if p != os.curdir), time.localtime(st.st_mtime)[0:6])
    info.create_system = 3
    info.external_attr = (st.st_mode & 0xFFFF) << 16
    z.writestr(info, os.readlink(s.encode(FS_ENCODING)))
  else:
    mode = zipfile.ZIP_DEFLATED
    if os.path.splitext(src[-1])[1][1:].lower() in ALREADY_COMPRESSEDS:
      mode = zipfile.ZIP_STORED
    z.write(s, os.path.join(*dst), mode)

startZip("diffs.zip")

# Copies files to be backed up to the current directory
mkdir((u'.',))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'Created File.txt'), (u'.', u'Created File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'Cross-Moved and Edited File.txt'), (u'.', u'Cross-Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'New Moved and Edited File.txt'), (u'.', u'New Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'Unmoved and Edited File.txt'), (u'.', u'Unmoved and Edited File.txt'))
mkdir((u'.', u'A Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'Created File.txt'), (u'.', u'A Subdirectory', u'Created File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'New Moved and Edited File.txt'), (u'.', u'A Subdirectory', u'New Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'A Subdirectory', u'Unmoved and Edited File.txt'), (u'.', u'A Subdirectory', u'Unmoved and Edited File.txt'))
mkdir((u'.', u'Created Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'Created Subdirectory', u'Created File.txt'), (u'.', u'Created Subdirectory', u'Created File.txt'))
mkdir((u'.', u'New Moved Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'New Moved Subdirectory', u'Double Cross-Moved and Edited File.txt'), (u'.', u'New Moved Subdirectory', u'Double Cross-Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src1', u'.', u'New Moved Subdirectory', u'Moved and Edited File.txt'), (u'.', u'New Moved Subdirectory', u'Moved and Edited File.txt'))
# Diff set file count: 10
# Diff set total bytes: 981

endZip()