chcp 1252
REM Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state
REM Copies duplicated updated files to all destinations
COPY ".\Deleted File.txt" ".\Lying File.txt"
COPY ".\Deleted File.txt" ".\A Subdirectory\Deleted File.txt"
COPY ".\Deleted File.txt" ".\A Subdirectory\Moved Lying File.txt"
COPY ".\Moved and Edited File.txt" ".\A Subdirectory\Moved and Edited File.txt"
COPY ".\Unmoved and Edited File.txt" ".\A Subdirectory\Unmoved and Edited File.txt"
COPY ".\Unmoved and Unedited File.txt" ".\A Subdirectory\Unmoved & Unedited File.txt"
