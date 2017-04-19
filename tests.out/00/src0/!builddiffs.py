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
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Another Unmoved and Unedited File.txt'), (u'.', u'Another Unmoved and Unedited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Deleted File.txt'), (u'.', u'Deleted File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Moved and Edited File.txt'), (u'.', u'Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Moved and Unedited File.txt'), (u'.', u'Moved and Unedited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Swapped File.txt'), (u'.', u'Swapped File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Unmoved and Edited File.txt'), (u'.', u'Unmoved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Unmoved and Unedited File.txt'), (u'.', u'Unmoved and Unedited File.txt'))
mkdir((u'.', u'A Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'A Subdirectory', u'Cross-Moved and Edited File.txt'), (u'.', u'A Subdirectory', u'Cross-Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'A Subdirectory', u'Cross-Moved and Unedited File.txt'), (u'.', u'A Subdirectory', u'Cross-Moved and Unedited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'A Subdirectory', u'Moved and Unedited File.txt'), (u'.', u'A Subdirectory', u'Moved and Unedited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'A Subdirectory', u'Swapped File.txt'), (u'.', u'A Subdirectory', u'Swapped File.txt'))
mkdir((u'.', u'Deleted Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Deleted Subdirectory', u'Deleted File.txt'), (u'.', u'Deleted Subdirectory', u'Deleted File.txt'))
mkdir((u'.', u'Moved Subdirectory'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Moved Subdirectory', u'Deleted File.txt'), (u'.', u'Moved Subdirectory', u'Deleted File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Moved Subdirectory', u'Moved and Edited File.txt'), (u'.', u'Moved Subdirectory', u'Moved and Edited File.txt'))
cp((u'/', u'tmp', u'TransparentBackup', u'tests.in', u'00', u'src0', u'.', u'Moved Subdirectory', u'Moved and Unedited File.txt'), (u'.', u'Moved Subdirectory', u'Moved and Unedited File.txt'))
# Diff set file count: 15
# Diff set total bytes: 1156

endZip()