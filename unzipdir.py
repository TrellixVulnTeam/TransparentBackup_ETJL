# -*- coding: iso-8859-1 -*-
import sys
import zipfile
import os
import os.path
import time



def main (args):
  syntax="Syntax: unzipdir <zipfile> <outputdir>"
  if len(args) != 2:
    sys.exit(syntax)
  zipFilePathName = args[0]
  outputDirPathName = args[1]

  t = time.time()
  z = zipfile.ZipFile(zipFilePathName, 'r')
  if not os.path.isdir(outputDirPathName):
    os.makedirs(outputDirPathName)
  for zinfo in z.infolist():
    z.extract(zinfo, outputDirPathName)
    pathName = os.path.join(outputDirPathName, zinfo.filename)
    os.utime(pathName, (t, time.mktime(zinfo.date_time + (-1, -1, -1))))
  z.close()



if __name__=="__main__":
  main([arg.decode(sys.stdin.encoding) for arg in sys.argv[1:]])
