@ECHO OFF
mkdir tests.new\00\src0
mkdir tests.new\00\src1
transparentbackup.py -b tests.in\00\src0 -o tests.new\00\src0 -s BatchFile
transparentbackup.py -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1 -s BatchFile
transparentbackup.py -b tests.in\00\src0 -o tests.new\00\src0 -s BashScript
transparentbackup.py -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1 -s BashScript
