# Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
# Copies duplicated updated files to all destinations
cp --no-dereference --preserve=all "./Deleted File.txt" "./Lying File.txt"
cp --no-dereference --preserve=all "./Deleted File.txt" "./A Subdirectory/Deleted File.txt"
cp --no-dereference --preserve=all "./Deleted File.txt" "./A Subdirectory/Moved Lying File.txt"
cp --no-dereference --preserve=all "./Moved and Edited File.txt" "./A Subdirectory/Moved and Edited File.txt"
cp --no-dereference --preserve=all "./Unmoved and Edited File.txt" "./A Subdirectory/Unmoved and Edited File.txt"
cp --no-dereference --preserve=all "./Unmoved and Unedited File.txt" "./A Subdirectory/Unmoved & Unedited File.txt"
