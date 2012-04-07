# -*- coding: iso-8859-1 -*-
#  -------------------------------------------------------------------
#  Transparent Backup 1.1.0                       PYTHON COMPONENTS
#  © Geoff Crossland 2005
#
#  1.0.0:
#  Compares a directory tree with a DTML file and creates data
#  about the differences between them.
#
#  1.1.0:
# -----------------------------------------------------------------  #
import time
import sys
import string
import getopt
import os
import md5
import cgi
import sgmllib
import xml.sax.saxutils



TMPDIR=".tmp"



def main (args):
  syntax="Syntax: transparentbackup [-b|--backup-source <backupdir>] [-d|--diff-dtml <dtmlfile>] [-o|--output <outputdir>] [-s|--scripttype <script type>]"
  (optlist,leftargs)=getopt.getopt(args,"b:d:o:s:",["backup-source=","diff-dtml=","output=","scripttype="])
  if len(leftargs)>0:
    sys.exit("Unknown arguments on command line ('"+str(leftargs)+"')\n"+syntax)
  opt_backup_source=None
  opt_diff_dtml=None
  opt_output=None
  opt_scripttype=None
  for (option,value) in optlist:
    if option in ("-b","--backup-source"):
      opt_backup_source=value
    if option in ("-d","--diff-dtml"):
      opt_diff_dtml=value
    if option in ("-o","--output"):
      opt_output=value
    if option in ("-s","--scripttype"):
      opt_scripttype=value
  if opt_backup_source==None:
    sys.exit("No backup source path (-b) supplied\n"+syntax)
  if not os.path.isdir(opt_backup_source):
    sys.exit("Backup source path (-b) is not a directory\n"+syntax)
  if opt_output==None:
    sys.exit("No output path (-o) supplied\n"+syntax)
  if not os.path.isdir(opt_output):
    sys.exit("Output path (-o) is not a directory\n"+syntax)
  if opt_scripttype==None:
    sys.exit("No script type (-s) supplied\n"+syntax)
  opt_backup_source=os.path.abspath(opt_backup_source)
  if opt_diff_dtml!=None:
    opt_diff_dtml=os.path.abspath(opt_diff_dtml)

  print "Backup source: "+opt_backup_source
  print "DTML file: "+str(opt_diff_dtml)
  opt_output=os.path.abspath(opt_output)
  print "Output: "+opt_output

  os.stat_float_times(True)

  transparentbackup(opt_backup_source,opt_diff_dtml,opt_output,opt_scripttype)



def transparentbackup (new_pathname,old_dtml,output_pathname,scripttype):
  if old_dtml==None:
    oldtree=DirectoryTree.gen_empty()
  else:
    oldtree=DirectoryTree.gen_dtml(old_dtml)
  newtree=DirectoryTree.gen_fs(new_pathname,oldtree)
  DirectoryTree.relname_cache=None
  ScriptDirectoryTreeDiffer().diff(oldtree,newtree,new_pathname,output_pathname,scripttype)
  newtree.writedtml(os.path.join(output_pathname,"!fullstate.dtml"))



def latin1isprintable (index):
  assert index>=0
  assert index<256
  return (index & 0x60)!=0


quick=0
slow=0

class DirectoryTree:
  relname_cache={}
  def relname_get (relname):
    return DirectoryTree.relname_cache.setdefault(relname,relname)
  relname_get=staticmethod(relname_get)

  def __init__ (self,root):
    self.root=root

  def gen_empty ():
    root=Directory(None,[])
    root.relname=DirectoryTree.relname_get(".")
    return DirectoryTree(root)
  gen_empty=staticmethod(gen_empty)

  def gen_fs (source_pathname,oldtree):
    (t,source_leafname)=os.path.split(source_pathname)
    if len(source_leafname)==0:
      sys.exit("Error while reading backup source: the pathname appears to have a directory seperator on the end (if refering to a directory, omit this)")
    root=DirectoryTree.gen_fs_dir(None,source_pathname,".",oldtree.root)
    root.relname=DirectoryTree.relname_get(".")
    return DirectoryTree(root)
  gen_fs=staticmethod(gen_fs)

  def gen_fs_dir (source_leafname,source_pathname,source_relname,oldtree):
    global quick,slow
    oldtreeSubobjs={}
    if oldtree:
      assert isinstance(oldtree,Directory)
      for subobj in oldtree.subobjs:
        oldtreeSubobjs[subobj.leafname]=subobj
    subobjs=os.listdir(source_pathname)
    subobjs.sort()
    i=0
    while i<len(subobjs):
      leafname=subobjs[i]
      for chr in leafname:
        if not latin1isprintable(ord(chr)):
          sys.exit("Error in DirectoryTree: unable to support file or directory with name '"+leafname+"', which contains a control character (might be a Unicode name which happens to be valid Windows-1252 but not valid Latin-1)")
      pathname=os.path.join(source_pathname,leafname)
      relname=DirectoryTree.relname_get(os.path.join(source_relname,leafname))
      oldtreeSubobj=oldtreeSubobjs.get(leafname,None)
      if os.path.isdir(pathname):
        if not isinstance(oldtreeSubobj,Directory):
          oldtreeSubobj=None
        subobj=DirectoryTree.gen_fs_dir(leafname,pathname,relname,oldtreeSubobj)
      else:
        if not isinstance(oldtreeSubobj,File):
          oldtreeSubobj=None
        weakSignature=WeakSignature.gen_fs(pathname)
        if oldtreeSubobj and oldtreeSubobj.weakSignature==weakSignature:
          #print "assuming that "+relname+" is unchanged"
          strongSignature=oldtreeSubobj.strongSignature
          quick+=1
        else:
          #print "recalculating strong sig for "+relname
          strongSignature=StrongSignature.gen_fs(pathname)
          slow+=1
        subobj=File(leafname,weakSignature,strongSignature)
      subobj.relname=relname
      subobjs[i]=subobj
      i=i+1
    return Directory(source_leafname,subobjs)
  gen_fs_dir=staticmethod(gen_fs_dir)

  def gen_dtml (pathname):
    return DirectoryTree(DirectoryTree_DTMLParser(pathname).root)
  gen_dtml=staticmethod(gen_dtml)

  def writedtml (self,pathname):
    file=open(pathname,"wb")
    file.write("<DTML>\n")
    for subobj in self.root.subobjs:
      subobj.writedtml(file,2)
    file.write("</DTML>")
    file.close()



class DirectoryTree_DTMLParser(sgmllib.SGMLParser):
  def processattrs (attrs):
    result={}
    for (name,value) in attrs:
      result[name]=xml.sax.saxutils.unescape(value)
    return result
  processattrs=staticmethod(processattrs)

  def __init__ (self,pathname):
    sgmllib.SGMLParser.__init__(self)
    self.dirleafnamestack=[]
    self.dirrelnamestack=[]
    self.subobjstack=[]

    file=open(pathname,"rb")
    data=file.read()
    file.close()

    self.dirrelnamestack.append(".")
    self.subobjstack.append([])

    self.feed(data)
    self.close()

    assert len(self.subobjstack)==len(self.dirrelnamestack)
    if len(self.subobjstack)!=1:
      sys.exit("Error in DirectoryTree: while parsing a DTML file, found that DIR tags had not been closed")
    assert len(self.dirleafnamestack)==0
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    self.root=Directory(None,subobjs)
    self.root.relname=DirectoryTree.relname_get(".")

  def report_unbalanced (self,tag):
    sys.exit("Error in DirectoryTree: while parsing a DTML file, found an end '"+tag+"' tag without a start tag")

  def start_dir (self,attrs):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      sys.exit("Error in DirectoryTree: DIR without name (attributes are "+str(attrs)+")")
    self.dirleafnamestack.append(attrs["name"])
    self.dirrelnamestack.append(DirectoryTree.relname_get(os.path.join(self.dirrelnamestack[-1],attrs["name"])))
    self.subobjstack.append([])

  def end_dir (self):
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    dir=Directory(self.dirleafnamestack.pop(),subobjs)
    dir.relname=self.dirrelnamestack.pop()
    self.subobjstack[-1].append(dir)

  def do_file (self,attrs):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      sys.exit("Error in DirectoryTree: FILE without name (attributes are "+str(attrs)+")")
    file=File(attrs["name"],WeakSignature.gen_dtml(attrs),StrongSignature.gen_dtml(attrs))
    file.relname=DirectoryTree.relname_get(os.path.join(self.dirrelnamestack[-1],attrs["name"]))
    self.subobjstack[-1].append(file)



class Object:
  def __init__ (self,leafname):
    if leafname==chr(255):
      sys.exit("Error in Object: unable to support file or directory with name '"+leafname+"', which begins with chr(255)")
    elif leafname==TMPDIR:
      sys.exit("Error in Object: unable to support file or directory with name '"+leafname+"', because this clashes with the temporary directory name")
    self.leafname=leafname

  def __cmp__ (self,other):
    if other==None:
      return 1
    return cmp(self.leafname,other.leafname)

  def writedtml (self,file,depth):
    raise NotImplementedError



class SentinelObject:
  def __init__ (self):
    self.leafname=chr(255)



sentinelobj=SentinelObject()



class Directory(Object):
  def __init__ (self,leafname,subobjs):
    Object.__init__(self,leafname)
    #print "Creating Directory '"+str(leafname)+"'"
    self.subobjs=subobjs

  def writedtml (self,file,depth):
    file.write(" "*depth)
    file.write("<DIR name=\"")
    file.write(cgi.escape(self.leafname,True))
    file.write("\">\n")
    for subobj in self.subobjs:
      subobj.writedtml(file,depth+2)
    file.write(" "*depth)
    file.write("</DIR>\n")



class File(Object):
  def __init__ (self,leafname,weakSignature,strongSignature):
    Object.__init__(self,leafname)
    #print "Creating File '"+str(leafname)+"'"
    self.weakSignature=weakSignature
    self.strongSignature=strongSignature

  def writedtml (self,file,depth):
    file.write(" "*depth)
#   file.write("<FILE name=")
#   file.write(xml.sax.saxutils.quoteattr(self.leafname))
    file.write("<FILE name=\"")
    file.write(cgi.escape(self.leafname,True))
    file.write("\"")
    attrs={}
    self.weakSignature.getdtml(attrs)
    self.strongSignature.getdtml(attrs)
    for name in ["size", "md5sum", "time"]:
      file.write(" "+name+"=")
      file.write(attrs[name])
    file.write(">\n")



class WeakSignature:
  def __init__ (self,size,lastModifiedTime):
    self.size=int(size)
    if self.size<0:
      sys.exit("Error in WeakSignature: initialised with size '"+str(size)+"', which is invalid")
    self.lastModifiedTime=int(lastModifiedTime)

  def gen_fs (pathname):
    #print "Creating WeakSignature for '"+str(pathname)+"'"
    fileInfo=os.stat(pathname)
    size=fileInfo.st_size
    #print "  size is "+str(size)
    lastModifiedTime=int(fileInfo.st_mtime*1000)
    #print "  lastModifiedTime is "+str(lastModifiedTime)
    return WeakSignature(size,lastModifiedTime)
  gen_fs=staticmethod(gen_fs)

  def gen_dtml (attrs):
    if not attrs.has_key("size") or not attrs.has_key("time"):
      sys.exit("Error in WeakSignature.gen_dtml: size and time attributes both required")
    return WeakSignature(attrs["size"],attrs["time"])
  gen_dtml=staticmethod(gen_dtml)

  def __cmp__ (self,other):
    if other==None:
      return 1
    if self.size<other.size:
      return -1
    if self.size>other.size:
      return 1
    if self.lastModifiedTime<other.lastModifiedTime:
      return -1
    if self.lastModifiedTime>other.lastModifiedTime:
      return 1
    return 0

  def __hash__ (self):
    return (self.size^self.lastModifiedTime)

  def getdtml (self,attrs):
    attrs["size"]=str(self.size)
    attrs["time"]=str(self.lastModifiedTime)



def renderMd5sum(val):
  assert isinstance(val,str)
  assert len(val)==16
  return "".join([hex(ord(c))[2:].upper().zfill(2) for c in val])



def parseMd5sum(val):
  val=str(val)
  assert len(val)==32
  return "".join([chr(int(val[i:i+2],16)) for i in xrange(0,32,2)])



class StrongSignature:
  def __init__ (self,size,md5sum):
    self.size=int(size)
    if self.size<0:
      sys.exit("Error in StrongSignature: initialised with size '"+str(size)+"', which is invalid")
    self.md5sum=md5sum

  def gen_fs (pathname):
    #print "Creating StrongSignature for '"+str(pathname)+"'"
    size=os.stat(pathname).st_size
    #print "  size is "+str(size)
    md5sum=md5.new()
    file=open(pathname,"rb")
    consumed=0
    while True:
      block=file.read(256*1024)
      if len(block)==0:
        break
      consumed=consumed+len(block)
      md5sum.update(block)
    file.close()
    if consumed!=size:
      sys.exit("Error while reading file for hashing: file '"+pathname+"' not properly read")
    #print "  md5sum is "+renderMd5sum(md5sum.digest())
    return StrongSignature(size,md5sum.digest())
  gen_fs=staticmethod(gen_fs)

  def gen_dtml (attrs):
    if not attrs.has_key("size") or not attrs.has_key("md5sum"):
      sys.exit("Error in StrongSignature.gen_dtml: size and md5sum attributes both required")
    return StrongSignature(attrs["size"],parseMd5sum(attrs["md5sum"]))
  gen_dtml=staticmethod(gen_dtml)

  def __cmp__ (self,other):
    if other==None:
      return 1
    if self.size<other.size:
      return -1
    if self.size>other.size:
      return 1
    if self.md5sum<other.md5sum:
      return -1
    if self.md5sum>other.md5sum:
      return 1
    return 0

  def __hash__ (self):
    return (self.size^self.md5sum.__hash__())

  def getdtml (self,attrs):
    attrs["size"]=str(self.size)
    attrs["md5sum"]=renderMd5sum(self.md5sum)



class DirectoryTreeDiffer:
  STATUS_UNMODIFIED=0
  STATUS_MODIFIED=1
  STATUS_DELETED=2

  def diff_dir (self,olddir,newdir,files):
    assert olddir.leafname==newdir.leafname
    assert isinstance(olddir,Directory)
    assert isinstance(newdir,Directory)

    # First, process files
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,File)]+[sentinelobj]
    old=oldsubobjs[0]
    oldindex=1
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,File)]+[sentinelobj]
    new=newsubobjs[0]
    newindex=1
    while old!=sentinelobj or new!=sentinelobj:
      if old.leafname==new.leafname:
        # An old file still exists
        if old.strongSignature!=new.strongSignature:
          self.file_modified(old,new,newdir,files)
        else:
          self.file_unmodified(old,new,files)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
        new=newsubobjs[newindex]
        newindex=newindex+1
      elif old.leafname<new.leafname:
        # An old file no longer exists
        self.file_del(old,files)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
      else:
        # A new file has been created
        self.file_gen(new,newdir,files)
        new=newsubobjs[newindex]
        newindex=newindex+1

    # Then, process directories
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,Directory)]+[sentinelobj]
    old=oldsubobjs[0]
    oldindex=1
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,Directory)]+[sentinelobj]
    new=newsubobjs[0]
    newindex=1
    while old!=sentinelobj or new!=sentinelobj:
      if old.leafname==new.leafname:
        # An old directory still exists
        self.dir_unmodified(old,new,files)
        self.diff_dir(old,new,files)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
        new=newsubobjs[newindex]
        newindex=newindex+1
      elif old.leafname<new.leafname:
        # An old directory no longer exists
        self.diff_dir_del(old,files)
        self.dir_del(old,files)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
      else:
        # A new directory has been created
        self.dir_gen(new,files)
        self.diff_dir_gen(new,files)
        new=newsubobjs[newindex]
        newindex=newindex+1

  def diff_dir_gen (self,newdir,files):
    assert isinstance(newdir,Directory)

    # First, process files
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,File)]
    for new in newsubobjs:
      self.file_gen(new,newdir,files)

    # Then, process directories
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,Directory)]
    for new in newsubobjs:
      self.dir_gen(new,files)
      self.diff_dir_gen(new,files)

  def diff_dir_del (self,olddir,files):
    assert isinstance(olddir,Directory)

    # First, process files
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,File)]
    for old in oldsubobjs:
      self.file_del(old,files)

    # Then, process directories
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,Directory)]
    for old in oldsubobjs:
      self.diff_dir_del(old,files)
      self.dir_del(old,files)

  def dir_gen (self,newobj,files):
    raise NotImplementedError

  def dir_del (self,oldobj,files):
    raise NotImplementedError

  def dir_unmodified (self,oldobj,newobj,files):
    raise NotImplementedError

  def file_gen (self,newobj,newdir,files):
    raise NotImplementedError

  def file_del (self,oldobj,files):
    raise NotImplementedError

  def file_modified (self,oldobj,newobj,newdir,files):
    raise NotImplementedError

  def file_unmodified (self,oldobj,newobj,files):
    raise NotImplementedError



class ScriptFile:
  def mkdir (self,name):
    raise NotImplementedError

  def comment (self,body):
    raise NotImplementedError

  def rmdir (self,name):
    raise NotImplementedError

  def cp (self,src,dst):
    raise NotImplementedError

  def mv (self,src,dst):
    raise NotImplementedError

  def rm (self,name):
    raise NotImplementedError

  def close (self):
    raise NotImplementedError



class BatchFile(ScriptFile):
  def __init__ (self,filename):
    self.file=open(filename+".bat","wb")
    self.file.write("chcp 1252\n")

  def comment (self,body):
    self.file.write("REM ")
    self.file.write(body)
    self.file.write("\n")

  def mkdir (self,name):
    self.file.write("MKDIR \"")
    self.file.write(name.replace("%","%%"))
    self.file.write("\"\n")

  def rmdir (self,name):
    self.file.write("RMDIR \"")
    self.file.write(name.replace("%","%%"))
    self.file.write("\"\n")

  def cp (self,src,dst):
    self.file.write("COPY \"")
    self.file.write(src.replace("%","%%"))
    self.file.write("\" \"")
    self.file.write(dst.replace("%","%%"))
    self.file.write("\"\n")

  def mv (self,src,dst):
    self.file.write("MOVE \"")
    self.file.write(src.replace("%","%%"))
    self.file.write("\" \"")
    self.file.write(dst.replace("%","%%"))
    self.file.write("\"\n")

  def rm (self,name):
    self.file.write("DEL /F \"")
    self.file.write(name.replace("%","%%"))
    self.file.write("\"\n")

  def close (self):
    self.file.close()



class BashScript(ScriptFile):
  def esc (s):
    return s.replace("\\","\\\\").replace("$","\\$").replace("`","\\$").replace("\"","\\\"")
  esc=staticmethod(esc)

  def winpathmap (path):
    if len(path)>1 and path[0].isalpha() and path[1]==":":
      path="/cygdrive/"+path[0].lower()+path[2:]
    return path.replace("\\","/")
  winpathmap=staticmethod(winpathmap)

  def __init__ (self,filename):
    self.file=open(filename+".sh","wb")

  def comment (self,body):
    self.file.write("# ")
    self.file.write(body)
    self.file.write("\n")

  def mkdir (self,name):
    self.file.write("mkdir --parents \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(name)))
    self.file.write("\"\n")

  def rmdir (self,name):
    self.file.write("rmdir \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(name)))
    self.file.write("\"\n")

  def cp (self,src,dst):
    self.file.write("cp \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(src)))
    self.file.write("\" \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(dst)))
    self.file.write("\"\n")

  def mv (self,src,dst):
    self.file.write("mv \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(src)))
    self.file.write("\" \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(dst)))
    self.file.write("\"\n")

  def rm (self,name):
    self.file.write("rm -f \"")
    self.file.write(BashScript.esc(BashScript.winpathmap(name)))
    self.file.write("\"\n")

  def close (self):
    self.file.close()



class ScriptDirectoryTreeDiffer(DirectoryTreeDiffer):
  class Files:
    def __init__ (self):
      self.oldfiles={}
      self.newfiles={}

  def diff (self,oldtree,newtree,new_pathname,output_pathname,scripttype):
    self.new_pathname=new_pathname

    name=os.path.join(output_pathname,"!builddiffs")
    self.builddiffs_file=eval(scripttype+"(name)")
    assert isinstance(self.builddiffs_file,ScriptFile)
    self.builddiffs_file.comment("Copies files to be backed up to the current directory")
    name=os.path.join(output_pathname,"!pre_applydiffs")
    self.preapplydiffs_file=eval(scripttype+"(name)")
    assert isinstance(self.preapplydiffs_file,ScriptFile)
    self.preapplydiffs_file.comment("Prepares the previous state of the backup set, rooted in the current directory, for having the updated files copied over it")
    name=os.path.join(output_pathname,"!post_applydiffs")
    self.postapplydiffs_file=eval(scripttype+"(name)")
    assert isinstance(self.postapplydiffs_file,ScriptFile)
    self.postapplydiffs_file.comment("Converts the aggregation of the previous state of the backup set and the updated files, rooted in the current directory, to the final new state")

    self.builddiffs_files_count=0
    self.builddiffs_files_size=0
    files=ScriptDirectoryTreeDiffer.Files()
    self.diff_pre_old(oldtree.root,files.oldfiles)
    self.diff_pre_new(newtree.root)
    self.diff_dir(oldtree.root,newtree.root,files)
    self.preapplydiffs_file.comment("Transfers copied files to temporary dirs")
    self.diff_post_stage(oldtree.root)
    self.preapplydiffs_file.comment("Transfers copied files to final destination")
    self.diff_post_copy(oldtree.root)
    self.preapplydiffs_file.comment("Clears away deleted objects and temporary dirs")
    self.diff_post_clear(oldtree.root)
    self.postapplydiffs_file.comment("Copies duplicated updated files to all destinations")
    self.diff_post_copynew(newtree.root)
    self.builddiffs_file.comment("Diff set file count: "+str(self.builddiffs_files_count))
    self.builddiffs_file.comment("Diff set total bytes: "+str(self.builddiffs_files_size))

    self.builddiffs_file.close()
    self.preapplydiffs_file.close()
    self.postapplydiffs_file.close()

  def diff_pre_old (self,olddir,files):
    assert isinstance(olddir,Directory)

    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,File):
        files[oldsubobj.strongSignature]=oldsubobj
        oldsubobj.copies=[]
      elif isinstance(oldsubobj,Directory):
        self.diff_pre_old(oldsubobj,files)

  def diff_pre_new (self,newdir):
    assert isinstance(newdir,Directory)

    for newsubobj in newdir.subobjs:
      if isinstance(newsubobj,File):
        newsubobj.copies=[]
      elif isinstance(newsubobj,Directory):
        self.diff_pre_new(newsubobj)

  def diff_post_stage (self,olddir):
    assert isinstance(olddir,Directory)

    tmpdir=None
    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,File):
        if len(oldsubobj.copies)>0:
          if tmpdir==None:
            tmpdir=os.path.join(olddir.relname,TMPDIR)
            self.preapplydiffs_file.mkdir(tmpdir)
          if oldsubobj.status==DirectoryTreeDiffer.STATUS_MODIFIED:
            method=self.preapplydiffs_file.mv
          elif oldsubobj.status==DirectoryTreeDiffer.STATUS_DELETED:
            method=self.preapplydiffs_file.mv
            oldsubobj.status=DirectoryTreeDiffer.STATUS_MODIFIED
          else:
            method=self.preapplydiffs_file.cp
          method(oldsubobj.relname,os.path.join(tmpdir,oldsubobj.leafname))
    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,Directory):
        self.diff_post_stage(oldsubobj)
    olddir.tmpdir=tmpdir

  def diff_post_copy (self,olddir):
    assert isinstance(olddir,Directory)

    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,File):
        if len(oldsubobj.copies)>0:
          tmpname=os.path.join(olddir.tmpdir,oldsubobj.leafname)
          for copy in oldsubobj.copies[0:-1]:
            self.preapplydiffs_file.cp(tmpname,copy.relname)
          self.preapplydiffs_file.mv(tmpname,oldsubobj.copies[-1].relname)
    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,Directory):
        self.diff_post_copy(oldsubobj)

  def diff_post_clear (self,olddir):
    assert isinstance(olddir,Directory)

    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,File):
        if oldsubobj.status==DirectoryTreeDiffer.STATUS_DELETED:
          self.preapplydiffs_file.rm(oldsubobj.relname)
    for oldsubobj in olddir.subobjs:
      if isinstance(oldsubobj,Directory):
        self.diff_post_clear(oldsubobj)
        if oldsubobj.status==DirectoryTreeDiffer.STATUS_DELETED:
          self.preapplydiffs_file.rmdir(oldsubobj.relname)
    if olddir.tmpdir!=None:
      self.preapplydiffs_file.rmdir(olddir.tmpdir)

  def diff_post_copynew (self,newdir):
    assert isinstance(newdir,Directory)

    for newsubobj in newdir.subobjs:
      if isinstance(newsubobj,File):
        for copy in newsubobj.copies:
          self.postapplydiffs_file.cp(newsubobj.relname,copy.relname)
    for newsubobj in newdir.subobjs:
      if isinstance(newsubobj,Directory):
        self.diff_post_copynew(newsubobj)

  def dir_gen (self,newobj,files):
    self.preapplydiffs_file.mkdir(newobj.relname)

  def dir_del (self,oldobj,files):
    oldobj.status=DirectoryTreeDiffer.STATUS_DELETED

  def dir_unmodified (self,oldobj,newobj,files):
    oldobj.status=DirectoryTreeDiffer.STATUS_UNMODIFIED

  def file_gen (self,newobj,newdir,files):
    obj=files.oldfiles.get(newobj.strongSignature,None)
    if obj==None:
      # The new file is not a direct copy of an old one
      obj=files.newfiles.get(newobj.strongSignature,None)
    if obj!=None:
      # The new file is a copy of an old one or another new one
      obj.copies.append(newobj)
    else:
      # The new file is neither a direct copy of an old one nor of a new one
      if not newdir.__dict__.has_key("inbuilddiffs"):
        self.builddiffs_file.mkdir(os.path.dirname(newobj.relname))
        newdir.inbuilddiffs=True
      self.builddiffs_file.cp(os.path.join(self.new_pathname,newobj.relname),newobj.relname)
      self.builddiffs_files_count=self.builddiffs_files_count+1
      self.builddiffs_files_size=self.builddiffs_files_size+newobj.strongSignature.size
      files.newfiles[newobj.strongSignature]=newobj

  def file_del (self,oldobj,files):
    oldobj.status=DirectoryTreeDiffer.STATUS_DELETED

  def file_modified (self,oldobj,newobj,newdir,files):
    oldobj.status=DirectoryTreeDiffer.STATUS_MODIFIED
    self.file_gen(newobj,newdir,files)

  def file_unmodified (self,oldobj,newobj,files):
    oldobj.status=DirectoryTreeDiffer.STATUS_UNMODIFIED



if __name__=="__main__":
  start=time.time()
  argv=sys.argv
  if len(argv)<2:
    main([])
  elif len(argv)==2:
    main(string.split(argv[1]))
  else:
    main(argv[1:])
  print "Took "+str(time.time()-start)+" secs"
  print "Of "+str(quick+slow)+" files, "+str((quick*100)/(quick+slow))+"% didn't need to be re-hashed"
