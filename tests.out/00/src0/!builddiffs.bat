REM Copies files to be backed up to the current directory
COPY "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Deleted File.txt" ".\Deleted File.txt"
COPY "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Moved and Edited File.txt" ".\Moved and Edited File.txt"
COPY "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Moved and Unedited File.txt" ".\Moved and Unedited File.txt"
COPY "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Unmoved and Edited File.txt" ".\Unmoved and Edited File.txt"
COPY "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Unmoved and Unedited File.txt" ".\Unmoved and Unedited File.txt"
XCOPY /E /I "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\A Subdirectory" ".\A Subdirectory"
XCOPY /E /I "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Deleted Subdirectory" ".\Deleted Subdirectory"
XCOPY /E /I "I:\--Geoff--\Software\apps\Transparent Backup.trunk\tests.in\00\src0\.\Moved Subdirectory" ".\Moved Subdirectory"
