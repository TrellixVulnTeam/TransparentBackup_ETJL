chcp 1252
REM Copies files to be backed up to the current directory
MKDIR "."
COPY "T:\tests.in\00\src0\.\Another Unmoved and Unedited File.txt" ".\Another Unmoved and Unedited File.txt"
COPY "T:\tests.in\00\src0\.\Deleted File.txt" ".\Deleted File.txt"
COPY "T:\tests.in\00\src0\.\Moved and Edited File.txt" ".\Moved and Edited File.txt"
COPY "T:\tests.in\00\src0\.\Moved and Unedited File.txt" ".\Moved and Unedited File.txt"
COPY "T:\tests.in\00\src0\.\Swapped File.txt" ".\Swapped File.txt"
COPY "T:\tests.in\00\src0\.\Unmoved and Edited File.txt" ".\Unmoved and Edited File.txt"
COPY "T:\tests.in\00\src0\.\Unmoved and Unedited File.txt" ".\Unmoved and Unedited File.txt"
MKDIR ".\A Subdirectory"
COPY "T:\tests.in\00\src0\.\A Subdirectory\Cross-Moved and Edited File.txt" ".\A Subdirectory\Cross-Moved and Edited File.txt"
COPY "T:\tests.in\00\src0\.\A Subdirectory\Cross-Moved and Unedited File.txt" ".\A Subdirectory\Cross-Moved and Unedited File.txt"
COPY "T:\tests.in\00\src0\.\A Subdirectory\Moved and Unedited File.txt" ".\A Subdirectory\Moved and Unedited File.txt"
COPY "T:\tests.in\00\src0\.\A Subdirectory\Swapped File.txt" ".\A Subdirectory\Swapped File.txt"
MKDIR ".\Deleted Subdirectory"
COPY "T:\tests.in\00\src0\.\Deleted Subdirectory\Deleted File.txt" ".\Deleted Subdirectory\Deleted File.txt"
MKDIR ".\Moved Subdirectory"
COPY "T:\tests.in\00\src0\.\Moved Subdirectory\Deleted File.txt" ".\Moved Subdirectory\Deleted File.txt"
COPY "T:\tests.in\00\src0\.\Moved Subdirectory\Moved and Edited File.txt" ".\Moved Subdirectory\Moved and Edited File.txt"
COPY "T:\tests.in\00\src0\.\Moved Subdirectory\Moved and Unedited File.txt" ".\Moved Subdirectory\Moved and Unedited File.txt"
REM Diff set file count: 15
REM Diff set total bytes: 1156
