# -*- coding: iso-8859-1 -*-
import sys
import os
import datetime
import urllib
import glob
import subprocess
import os.path
import shutil



def getBackupSetName(pathName):
  return urllib.quote(os.path.basename(pathName), safe = "")



def main (args):
  syntax = "Syntax: makebackups [path]..."
  if len(args) == 0:
    sys.exit(syntax)

  date = datetime.date.today()
  dateStr = str(date.year % 100).zfill(2) + str(date.month).zfill(2) + str(date.day).zfill(2)

  for backupSourcePathName in args:
    backupSetName = getBackupSetName(backupSourcePathName)
    t = glob.glob(backupSetName + "[0-9][0-9][0-9][0-9][0-9][0-9].dtml")
    if len(t) > 1:
      sys.exit("More than one DTML file found for " + backupSourcePathName + " (" + str(t) + ")")
    if len(t) == 0:
      dtmlFilePathName = None
      outputDirPathName = backupSetName + dateStr
    else:
      dtmlFilePathName = t[0]
      outputDirPathName = backupSetName + dateStr + "from" + dtmlFilePathName[len(backupSetName):-5]

    os.mkdir(outputDirPathName)
    tbArgs = [sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "transparentbackup.py"), "--backup-source", backupSourcePathName, "--output", outputDirPathName, "--scripttype", "PythonScript"]
    if dtmlFilePathName is not None:
      tbArgs += ["--diff-dtml", dtmlFilePathName]
    p = subprocess.Popen(tbArgs)
    rc = p.wait()
    if rc != 0:
      sys.exit("Backup of " + backupSourcePathName + " failed")

    tbArgs = [sys.executable, "!builddiffs.py"]
    p = subprocess.Popen(tbArgs, cwd = outputDirPathName)
    rc = p.wait()
    if rc != 0:
      sys.exit("!builddiffs.py for " + backupSourcePathName + " failed")

    shutil.copyfile(os.path.join(outputDirPathName, "!fullstate.dtml"), backupSetName + dateStr + ".dtml")
    if dtmlFilePathName is not None:
      os.remove(dtmlFilePathName)



if __name__ == "__main__":
  main(sys.argv[1:])
