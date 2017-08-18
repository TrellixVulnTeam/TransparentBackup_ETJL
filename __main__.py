#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  Transparent Backup
#  © Geoff Crossland 2005, 2012, 2014, 2017
# ------------------------------------------------------------------------------
import time
import sys
import getopt
import os
from transparentbackup import exit
import transparentbackup

def main (args):
  syntax="Syntax: transparentbackup [-b|--backup-source <backupdir>] [-d|--diff-dtml <dtmlfile>] [-o|--output <outputdir>] [-s|--scripttype <script type>] [--skip-suffix <suffix>]"
  (optlist, leftargs) = getopt.getopt(args, "b:d:o:s:", ["backup-source=", "diff-dtml=", "signatures-dtml=", "output=", "scripttype=", "skip-suffix="])
  if len(leftargs)>0:
    exit("Unknown arguments on command line ('"+unicode(leftargs)+"')\n"+syntax)
  opt_backup_source=None
  opt_diff_dtml=None
  opt_signatures_dtml = None
  opt_output=None
  opt_scripttype=None
  opt_skip_suffix=None
  for (option,value) in optlist:
    if option in ("-b","--backup-source"):
      opt_backup_source=value
      assert isinstance(opt_backup_source,unicode)
    if option in ("-d","--diff-dtml"):
      opt_diff_dtml=value
      assert isinstance(opt_diff_dtml,unicode)
    if option == "--signatures-dtml":
      opt_signatures_dtml = value
      assert isinstance(opt_signatures_dtml, unicode)
    if option in ("-o","--output"):
      opt_output=value
      assert isinstance(opt_output,unicode)
    if option in ("-s","--scripttype"):
      opt_scripttype=value
    if option=="--skip-suffix":
      opt_skip_suffix=value
  if opt_backup_source is None:
    exit("No backup source path (-b) supplied\n"+syntax)
  if not os.path.isdir(opt_backup_source):
    exit("Backup source path (-b) is not a directory\n"+syntax)
  if opt_output is None:
    exit("No output path (-o) supplied\n"+syntax)
  if not os.path.isdir(opt_output):
    exit("Output path (-o) is not a directory\n"+syntax)
  if opt_scripttype is None:
    exit("No script type (-s) supplied\n"+syntax)
  scripttypeCls = transparentbackup.getScripttypeCls(opt_scripttype)
  if not scripttypeCls:
    exit("Script type (-s) is not valid\n"+syntax)
  opt_backup_source=os.path.abspath(opt_backup_source)
  if opt_diff_dtml is not None and opt_signatures_dtml is not None:
    exit("Multiple DTML files supplied\n" + syntax)
  if opt_diff_dtml is not None:
    opt_diff_dtml=os.path.abspath(opt_diff_dtml)
  if opt_signatures_dtml is not None:
    opt_signatures_dtml = os.path.abspath(opt_signatures_dtml)

  print "Backup source: "+opt_backup_source
  print "DTML file: "+unicode(opt_diff_dtml)
  opt_output=os.path.abspath(opt_output)
  print "Output: "+opt_output

  transparentbackup.transparentbackup(opt_backup_source, opt_diff_dtml, opt_signatures_dtml, opt_skip_suffix, opt_output, scripttypeCls)

if __name__=="__main__":
  start=time.time()
  envEncoding = sys.stdin.encoding or sys.getdefaultencoding()
  main([arg.decode(envEncoding) for arg in sys.argv[1:]])
  print "Took "+unicode(time.time()-start)+" secs"
  print "Of "+unicode(transparentbackup.quick+transparentbackup.slow)+" files, "+unicode((transparentbackup.quick*100)/(transparentbackup.quick+transparentbackup.slow))+"% didn't need to be re-hashed"
