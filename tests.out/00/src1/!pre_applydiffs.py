
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
mkdir(('.', 'Created Subdirectory'))
mkdir(('.', 'New Moved Subdirectory'))
# Transfers copied files to temporary dirs
mkdir(('.', '.tmp'))
cp(('.', 'Another Unmoved and Unedited File.txt'), ('.', '.tmp', 'Another Unmoved and Unedited File.txt'))
cp(('.', 'Lying File.txt'), ('.', '.tmp', 'Lying File.txt'))
mv(('.', 'Moved and Unedited File.txt'), ('.', '.tmp', 'Moved and Unedited File.txt'))
mv(('.', 'Swapped File.txt'), ('.', '.tmp', 'Swapped File.txt'))
cp(('.', 'Unmoved and Unedited File.txt'), ('.', '.tmp', 'Unmoved and Unedited File.txt'))
mkdir(('.', 'A Subdirectory', '.tmp'))
mv(('.', 'A Subdirectory', 'Cross-Moved and Unedited File.txt'), ('.', 'A Subdirectory', '.tmp', 'Cross-Moved and Unedited File.txt'))
mv(('.', 'A Subdirectory', 'Moved and Unedited File.txt'), ('.', 'A Subdirectory', '.tmp', 'Moved and Unedited File.txt'))
mv(('.', 'A Subdirectory', 'Swapped File.txt'), ('.', 'A Subdirectory', '.tmp', 'Swapped File.txt'))
mkdir(('.', 'Moved Subdirectory', '.tmp'))
mv(('.', 'Moved Subdirectory', 'Moved and Unedited File.txt'), ('.', 'Moved Subdirectory', '.tmp', 'Moved and Unedited File.txt'))
# Transfers copied files to final destination
mv(('.', '.tmp', 'Another Unmoved and Unedited File.txt'), ('.', 'Copied Another Unmoved and Unedited File.txt'))
mv(('.', '.tmp', 'Lying File.txt'), ('.', 'Created Subdirectory', 'New Moved Lying File.txt'))
mv(('.', '.tmp', 'Moved and Unedited File.txt'), ('.', 'New Moved and Unedited File.txt'))
mv(('.', '.tmp', 'Swapped File.txt'), ('.', 'A Subdirectory', 'Swapped File.txt'))
cp(('.', '.tmp', 'Unmoved and Unedited File.txt'), ('.', 'Copied Unmoved and Unedited File.txt'))
cp(('.', '.tmp', 'Unmoved and Unedited File.txt'), ('.', 'A Subdirectory', 'Copied Unmoved & Unedited File.txt'))
mv(('.', '.tmp', 'Unmoved and Unedited File.txt'), ('.', 'New Moved Subdirectory', 'Cross-Copied Unmoved & Unedited File.txt'))
cp(('.', 'A Subdirectory', '.tmp', 'Cross-Moved and Unedited File.txt'), ('.', 'Cross-Moved and Unedited File.txt'))
mv(('.', 'A Subdirectory', '.tmp', 'Cross-Moved and Unedited File.txt'), ('.', 'New Moved Subdirectory', 'Double Cross-Moved and Unedited File.txt'))
mv(('.', 'A Subdirectory', '.tmp', 'Moved and Unedited File.txt'), ('.', 'A Subdirectory', 'New Moved and Unedited File.txt'))
mv(('.', 'A Subdirectory', '.tmp', 'Swapped File.txt'), ('.', 'Swapped File.txt'))
mv(('.', 'Moved Subdirectory', '.tmp', 'Moved and Unedited File.txt'), ('.', 'New Moved Subdirectory', 'Moved and Unedited File.txt'))
# Clears away deleted objects and temporary dirs
rm(('.', 'Deleted File.txt'))
rm(('.', 'Moved and Edited File.txt'))
rm(('.', 'A Subdirectory', 'Cross-Moved and Edited File.txt'))
rm(('.', 'A Subdirectory', 'Deleted File.txt'))
rm(('.', 'A Subdirectory', 'Moved Lying File.txt'))
rm(('.', 'A Subdirectory', 'Moved and Edited File.txt'))
rmdir(('.', 'A Subdirectory', '.tmp'))
rm(('.', 'Deleted Subdirectory', 'Deleted File.txt'))
rmdir(('.', 'Deleted Subdirectory'))
rm(('.', 'Moved Subdirectory', 'Deleted File.txt'))
rm(('.', 'Moved Subdirectory', 'Moved and Edited File.txt'))
rmdir(('.', 'Moved Subdirectory', '.tmp'))
rmdir(('.', 'Moved Subdirectory'))
rmdir(('.', '.tmp'))
