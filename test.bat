@ECHO OFF
transparentbackup.cmd -b tests.in\00\src0 -o tests.new\00\src0
transparentbackup.cmd -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1
