@ECHO OFF

subst T: .
cd /D T:

I:\Apps\Platforms\Cygwin\bin\rm.exe -rf "tests.in/00/src0"
mkdir tests.in\00\src0
cd tests.in\00\src0
I:\Apps\Platforms\Cygwin\bin\tar.exe -xf "../src0.tar"
cd ..\..\..

I:\Apps\Platforms\Cygwin\bin\rm.exe -rf "tests.in/00/src1"
mkdir tests.in\00\src1
cd tests.in\00\src1
I:\Apps\Platforms\Cygwin\bin\tar.exe -xf "../src1.tar"
cd ..\..\..

mkdir tests.new\00\src0
mkdir tests.new\00\src1
transparentbackup.py -b tests.in\00\src0 -o tests.new\00\src0 -s BatchFile --skip ".NOBACKUP"
transparentbackup.py -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1 -s BatchFile --skip ".NOBACKUP"
transparentbackup.py -b tests.in\00\src0 -o tests.new\00\src0 -s BashScript --skip ".NOBACKUP"
transparentbackup.py -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1 -s BashScript --skip ".NOBACKUP"
transparentbackup.py -b tests.in\00\src0 -o tests.new\00\src0 -s ZippingPythonScript --skip ".NOBACKUP"
transparentbackup.py -d tests.new\00\src0\!fullstate.dtml -b tests.in\00\src1 -o tests.new\00\src1 -s ZippingPythonScript --skip ".NOBACKUP"

subst /D T:
