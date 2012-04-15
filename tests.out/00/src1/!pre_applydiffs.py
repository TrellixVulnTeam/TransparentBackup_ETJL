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

# Prepares the previous state of the backup set, rooted in the current directory, for having the updated files copied over it
mkdir((u'.', u'Created Subdirectory'))
mkdir((u'.', u'New Moved Subdirectory'))
# Transfers copied files to temporary dirs
mkdir((u'.', u'.tmp'))
cp((u'.', u'Another Unmoved and Unedited File.txt'), (u'.', u'.tmp', u'Another Unmoved and Unedited File.txt'))
cp((u'.', u'Lying File.txt'), (u'.', u'.tmp', u'Lying File.txt'))
mv((u'.', u'Moved and Unedited File.txt'), (u'.', u'.tmp', u'Moved and Unedited File.txt'))
mv((u'.', u'Swapped File.txt'), (u'.', u'.tmp', u'Swapped File.txt'))
cp((u'.', u'Unmoved and Unedited File.txt'), (u'.', u'.tmp', u'Unmoved and Unedited File.txt'))
mkdir((u'.', u'A Subdirectory', u'.tmp'))
mv((u'.', u'A Subdirectory', u'Cross-Moved and Unedited File.txt'), (u'.', u'A Subdirectory', u'.tmp', u'Cross-Moved and Unedited File.txt'))
mv((u'.', u'A Subdirectory', u'Moved and Unedited File.txt'), (u'.', u'A Subdirectory', u'.tmp', u'Moved and Unedited File.txt'))
mv((u'.', u'A Subdirectory', u'Swapped File.txt'), (u'.', u'A Subdirectory', u'.tmp', u'Swapped File.txt'))
mkdir((u'.', u'Moved Subdirectory', u'.tmp'))
mv((u'.', u'Moved Subdirectory', u'Moved and Unedited File.txt'), (u'.', u'Moved Subdirectory', u'.tmp', u'Moved and Unedited File.txt'))
# Transfers copied files to final destination
mv((u'.', u'.tmp', u'Another Unmoved and Unedited File.txt'), (u'.', u'Copied Another Unmoved and Unedited File.txt'))
mv((u'.', u'.tmp', u'Lying File.txt'), (u'.', u'Created Subdirectory', u'New Moved Lying File.txt'))
mv((u'.', u'.tmp', u'Moved and Unedited File.txt'), (u'.', u'New Moved and Unedited File.txt'))
mv((u'.', u'.tmp', u'Swapped File.txt'), (u'.', u'A Subdirectory', u'Swapped File.txt'))
cp((u'.', u'.tmp', u'Unmoved and Unedited File.txt'), (u'.', u'Copied Unmoved and Unedited File.txt'))
cp((u'.', u'.tmp', u'Unmoved and Unedited File.txt'), (u'.', u'A Subdirectory', u'Copied Unmoved & Unedited File.txt'))
mv((u'.', u'.tmp', u'Unmoved and Unedited File.txt'), (u'.', u'New Moved Subdirectory', u'Cross-Copied Unmoved & Unedited File.txt'))
cp((u'.', u'A Subdirectory', u'.tmp', u'Cross-Moved and Unedited File.txt'), (u'.', u'Cross-Moved and Unedited File.txt'))
mv((u'.', u'A Subdirectory', u'.tmp', u'Cross-Moved and Unedited File.txt'), (u'.', u'New Moved Subdirectory', u'Double Cross-Moved and Unedited File.txt'))
mv((u'.', u'A Subdirectory', u'.tmp', u'Moved and Unedited File.txt'), (u'.', u'A Subdirectory', u'New Moved and Unedited File.txt'))
mv((u'.', u'A Subdirectory', u'.tmp', u'Swapped File.txt'), (u'.', u'Swapped File.txt'))
mv((u'.', u'Moved Subdirectory', u'.tmp', u'Moved and Unedited File.txt'), (u'.', u'New Moved Subdirectory', u'Moved and Unedited File.txt'))
# Clears away deleted objects and temporary dirs
rm((u'.', u'Deleted File.txt'))
rm((u'.', u'Moved and Edited File.txt'))
rm((u'.', u'A Subdirectory', u'Cross-Moved and Edited File.txt'))
rm((u'.', u'A Subdirectory', u'Deleted File.txt'))
rm((u'.', u'A Subdirectory', u'Moved Lying File.txt'))
rm((u'.', u'A Subdirectory', u'Moved and Edited File.txt'))
rmdir((u'.', u'A Subdirectory', u'.tmp'))
rm((u'.', u'Deleted Subdirectory', u'Deleted File.txt'))
rmdir((u'.', u'Deleted Subdirectory'))
rm((u'.', u'Moved Subdirectory', u'Deleted File.txt'))
rm((u'.', u'Moved Subdirectory', u'Moved and Edited File.txt'))
rmdir((u'.', u'Moved Subdirectory', u'.tmp'))
rmdir((u'.', u'Moved Subdirectory'))
rmdir((u'.', u'.tmp'))
