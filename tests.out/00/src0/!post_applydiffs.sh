# Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
# Copies duplicated updated files to all destinations
cp "./Deleted File.txt" "./A Subdirectory/Deleted File.txt"
cp "./Moved and Edited File.txt" "./A Subdirectory/Moved and Edited File.txt"
cp "./Moved and Unedited File.txt" "./A Subdirectory/Moved and Unedited File.txt"
cp "./Unmoved and Edited File.txt" "./A Subdirectory/Unmoved and Edited File.txt"
cp "./Unmoved and Unedited File.txt" "./A Subdirectory/Unmoved & Unedited File.txt"
