#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  Transparent Backup Wrapper
#  © Geoff Crossland 2012-2014
# ------------------------------------------------------------------------------
import sys
import os
import datetime
import urllib
import glob
import subprocess
import os.path
import shutil

BUILDER_LEAF_NAME = u"!builddiffs.py"
STATE_LEAF_NAME = u"!fullstate.dtml"

def exit (msg):
  isinstance(msg,basestring)
  try:
    m = str(msg)
  except:
    m = repr(msg)[2:-1]
  sys.exit(m)

def getBackupSetName (pathName):
  return urllib.quote(os.path.basename(pathName), safe = "")

def main (args):
  syntax = "Syntax: makebackups <root out dir> <mode> [path]..."
  if len(args) < 2:
    exit(syntax)

  date = datetime.date.today()
  dateStr = str(date.year % 100).zfill(2) + str(date.month).zfill(2) + str(date.day).zfill(2)

  rootOutputDirPathName = args[0]
  mode = args[1]
  for backupSourcePathName in args[2:]:
    backupSetName = getBackupSetName(backupSourcePathName)
    t = glob.glob(backupSetName + "[0-9][0-9][0-9][0-9][0-9][0-9].dtml")
    if len(t) > 1:
      exit("More than one DTML file found for " + backupSourcePathName + " (" + unicode(t) + ")")
    if len(t) == 0:
      dtmlFilePathName = None
      outputDirPathName = backupSetName + dateStr
    else:
      dtmlFilePathName = t[0]
      outputDirPathName = backupSetName + dateStr + "from" + dtmlFilePathName[len(backupSetName):-5]
    outputDirPathName = os.path.join(rootOutputDirPathName, outputDirPathName)

    os.mkdir(outputDirPathName)
    tbArgs = [sys.executable, os.path.join(os.path.dirname(sys.argv[0]), "transparentbackup.py"), "--backup-source", backupSourcePathName, "--output", outputDirPathName, "--scripttype", mode + "PythonScript", "--skip-suffix", ".NOBACKUP"]
    if dtmlFilePathName is not None:
      tbArgs += ["--diff-dtml", dtmlFilePathName]
    p = subprocess.Popen(tbArgs)
    rc = p.wait()
    if rc != 0:
      exit("Backup of " + backupSourcePathName + " failed")

    tbArgs = [sys.executable, BUILDER_LEAF_NAME]
    p = subprocess.Popen(tbArgs, cwd = outputDirPathName)
    rc = p.wait()
    if rc != 0:
      exit(BUILDER_LEAF_NAME + " for " + backupSourcePathName + " failed")
    os.remove(os.path.join(outputDirPathName, BUILDER_LEAF_NAME))

    if dtmlFilePathName is not None:
      shutil.move(dtmlFilePathName, dtmlFilePathName + ".old")
    shutil.move(os.path.join(outputDirPathName, STATE_LEAF_NAME), backupSetName + dateStr + ".dtml")

if __name__ == "__main__":
  envEncoding = sys.stdin.encoding or sys.getdefaultencoding()
  main([arg.decode(envEncoding) for arg in sys.argv[1:]])
