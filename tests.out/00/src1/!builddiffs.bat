chcp 1252
REM Copies files to be backed up to the current directory
COPY "T:\tests.in\00\src1\.\Created File.txt" ".\Created File.txt"
COPY "T:\tests.in\00\src1\.\Cross-Moved and Edited File.txt" ".\Cross-Moved and Edited File.txt"
COPY "T:\tests.in\00\src1\.\New Moved and Edited File.txt" ".\New Moved and Edited File.txt"
COPY "T:\tests.in\00\src1\.\Unmoved and Edited File.txt" ".\Unmoved and Edited File.txt"
MKDIR ".\A Subdirectory"
COPY "T:\tests.in\00\src1\.\A Subdirectory\Created File.txt" ".\A Subdirectory\Created File.txt"
COPY "T:\tests.in\00\src1\.\A Subdirectory\New Moved and Edited File.txt" ".\A Subdirectory\New Moved and Edited File.txt"
COPY "T:\tests.in\00\src1\.\A Subdirectory\Unmoved and Edited File.txt" ".\A Subdirectory\Unmoved and Edited File.txt"
MKDIR ".\Created Subdirectory"
COPY "T:\tests.in\00\src1\.\Created Subdirectory\Created File.txt" ".\Created Subdirectory\Created File.txt"
MKDIR ".\New Moved Subdirectory"
COPY "T:\tests.in\00\src1\.\New Moved Subdirectory\Double Cross-Moved and Edited File.txt" ".\New Moved Subdirectory\Double Cross-Moved and Edited File.txt"
COPY "T:\tests.in\00\src1\.\New Moved Subdirectory\Moved and Edited File.txt" ".\New Moved Subdirectory\Moved and Edited File.txt"
REM Diff set file count: 10
REM Diff set total bytes: 981
