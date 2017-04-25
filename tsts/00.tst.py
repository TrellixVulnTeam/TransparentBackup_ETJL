import transparentbackup
import os
import tarfile
import codecs
import difflib
import shutil

def readFile (pathName):
  if os.path.isfile(pathName):
    with codecs.open(pathName, 'r', 'utf-8') as f:
      return f.readlines()
  else:
    return []

def listDir (pathName):
  if not os.path.isdir(pathName):
    return ()
  return os.listdir(pathName)

D = "srcs*"

def T (data):
  srcs = sorted(listDir(data))

  DIR_PATH_NAME = u"/tmp/TransparentBackup"
  SRC_PATH_NAME = os.path.join(DIR_PATH_NAME, "src")
  OUT_PATH_NAME = os.path.join(DIR_PATH_NAME, "out")
  PREV_DTML_PATH_NAME = os.path.join(DIR_PATH_NAME, "prevsrc.dtml")
  CURR_DTML_PATH_NAME = os.path.join(DIR_PATH_NAME, "src.dtml")

  firstSrc = True
  for src in srcs:
    os.makedirs(SRC_PATH_NAME)
    with tarfile.open(os.path.join(data, src)) as tf:
      tf.extractall(SRC_PATH_NAME)

    firstScripttype = True
    for scripttypeCls in (transparentbackup.getScripttypeCls(p + "Script") for p in ("Bash", "ZippingPython")):
      t("Backing up {} with {}{}:", src, scripttypeCls.__name__, (" incrementally against prev", "")[firstSrc])
      os.makedirs(OUT_PATH_NAME)
      transparentbackup.transparentbackup(SRC_PATH_NAME, (PREV_DTML_PATH_NAME, None)[firstSrc], u".NOBACKUP", OUT_PATH_NAME, scripttypeCls)

      dtmlPathName = os.path.join(OUT_PATH_NAME, "!fullstate.dtml")
      builddiffsPathName = glob.glob(os.path.join(OUT_PATH_NAME, "!builddiffs.*"))[0]
      prePathName = glob.glob(os.path.join(OUT_PATH_NAME, "!pre_applydiffs.*"))[0]
      postPathName = glob.glob(os.path.join(OUT_PATH_NAME, "!post_applydiffs.*"))[0]
      if firstScripttype:
        t("dtml\n--------\n{}\n--------", "".join(readFile(dtmlPathName)))
      else:
        t("dtml diffs\n--------\n{}\n--------", "".join(difflib.unified_diff(readFile(CURR_DTML_PATH_NAME), readFile(dtmlPathName))))
      t("builddiffs\n--------\n{}\n--------", "".join(readFile(builddiffsPathName)))
      t("pre_applydiffs\n--------\n{}\n--------", "".join(readFile(prePathName)))
      t("post_applydiffs\n--------\n{}\n--------", "".join(readFile(postPathName)))

      if firstScripttype:
        os.rename(dtmlPathName, CURR_DTML_PATH_NAME)

      shutil.rmtree(OUT_PATH_NAME)
      firstScripttype = False

    os.rename(CURR_DTML_PATH_NAME, PREV_DTML_PATH_NAME)

    shutil.rmtree(SRC_PATH_NAME)
    firstSrc = False
