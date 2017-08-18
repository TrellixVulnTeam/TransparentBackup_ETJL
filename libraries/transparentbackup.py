# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#  Transparent Backup Library
#  © Geoff Crossland 2005, 2012, 2014, 2017
# ------------------------------------------------------------------------------
import sys
import os
import codecs
import hashlib
import cgi
import sgmllib
import xml.sax.saxutils

TMPDIR=u".tb-tmp"

def getScripttypeCls (scripttype):
  cls = globals().get(scripttype, None)
  if not isinstance(cls, type) or ScriptFile not in cls.__mro__:
    return None
  return cls

def exit (msg):
  isinstance(msg,basestring)
  try:
    m=str(msg)
  except:
    m=repr(msg)[2:-1]
  sys.exit(m)

def transparentbackup (new_pathname, old_dtml, signatures_dtml, skip_suffix, output_pathname, scripttypeCls):
  if old_dtml is None:
    oldtree=DirectoryTree.gen_empty()
  else:
    oldtree=DirectoryTree.gen_dtml(old_dtml)
  if signatures_dtml is None:
    signaturesTree = oldtree
  else:
    signaturesTree = DirectoryTree.gen_dtml(signatures_dtml)
  newtree=DirectoryTree.gen_fs(new_pathname, signaturesTree, skip_suffix)
  DirectoryTree.relname_cache={}
  ScriptDirectoryTreeDiffer().diff(oldtree,newtree,new_pathname,output_pathname,scripttypeCls)
  newtree.writedtml(os.path.join(output_pathname,u"!fullstate.dtml"))

quick=0
slow=0

class DirectoryTree (object):
  relname_cache={}
  def relname_get (relname):
    return DirectoryTree.relname_cache.setdefault(relname,relname)
  relname_get=staticmethod(relname_get)

  def __init__ (self,root):
    self.root=root

  def gen_empty ():
    root=Directory(None,[])
    root.relname=DirectoryTree.relname_get(u".")
    return DirectoryTree(root)
  gen_empty=staticmethod(gen_empty)

  def gen_fs (source_pathname,oldtree,skip_suffix):
    (t,source_leafname)=os.path.split(source_pathname)
    if len(source_leafname)==0:
      exit("Error while reading backup source: the pathname appears to have a directory seperator on the end (if referring to a directory, omit this)")
    root=DirectoryTree.gen_fs_dir(None,source_pathname,u".",oldtree.root,skip_suffix)
    root.relname=DirectoryTree.relname_get(u".")
    return DirectoryTree(root)
  gen_fs=staticmethod(gen_fs)

  def gen_fs_dir (source_leafname,source_pathname,source_relname,oldtree,skip_suffix):
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
      if skip_suffix and leafname.endswith(skip_suffix):
        del subobjs[i]
      else:
        pathname=os.path.join(source_pathname,leafname)
        relname=DirectoryTree.relname_get(os.path.join(source_relname,leafname))
        oldtreeSubobj=oldtreeSubobjs.get(leafname,None)
        isLink = os.path.islink(pathname)
        if not isLink and os.path.isdir(pathname):
          if not isinstance(oldtreeSubobj,Directory):
            oldtreeSubobj=None
          subobj=DirectoryTree.gen_fs_dir(leafname,pathname,relname,oldtreeSubobj,skip_suffix)
        elif isLink or os.path.isfile(pathname):
          fileCls = (RegularFile, Symlink)[isLink]
          if not isinstance(oldtreeSubobj, fileCls):
            oldtreeSubobj=None
          weakSignature = WeakSignature.gen_fs(pathname, fileCls)
          if oldtreeSubobj and oldtreeSubobj.weakSignature==weakSignature:
            strongSignature=oldtreeSubobj.strongSignature
            quick+=1
          else:
            strongSignature = StrongSignature.gen_fs(pathname, fileCls)
            slow+=1
          subobj = fileCls(leafname, weakSignature, strongSignature)
        else:
          exit("Error while reading backup source: file '" + pathname + "' is neither a link nor a regular file nor a directory")
        subobj.relname=relname
        subobjs[i]=subobj
        i=i+1
    return Directory(source_leafname,subobjs)
  gen_fs_dir=staticmethod(gen_fs_dir)

  def gen_dtml (pathname):
    return DirectoryTree(DirectoryTree_DTMLParser(pathname).root)
  gen_dtml=staticmethod(gen_dtml)

  def writedtml (self,pathname):
    file=codecs.open(pathname,'wb','utf-8')
    file.write(u"<DTML>\n")
    for subobj in self.root.subobjs:
      subobj.writedtml(file,2)
    file.write(u"</DTML>")
    file.close()

class DirectoryTree_DTMLParser (sgmllib.SGMLParser):
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

    file=codecs.open(pathname,'rb','utf-8')
    data=file.read()
    file.close()

    self.dirrelnamestack.append(u".")
    self.subobjstack.append([])

    self.feed(data)
    self.close()

    assert len(self.subobjstack)==len(self.dirrelnamestack)
    if len(self.subobjstack)!=1:
      exit("Error in DirectoryTree: while parsing a DTML file, found that DIR tags had not been closed")
    assert len(self.dirleafnamestack)==0
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    self.root=Directory(None,subobjs)
    self.root.relname=DirectoryTree.relname_get(u".")

  def report_unbalanced (self,tag):
    exit("Error in DirectoryTree: while parsing a DTML file, found an end '"+tag+"' tag without a start tag")

  def start_dir (self,attrs):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      exit("Error in DirectoryTree: DIR without name (attributes are "+unicode(attrs)+")")
    assert isinstance(attrs["name"],unicode)
    self.dirleafnamestack.append(attrs["name"])
    self.dirrelnamestack.append(DirectoryTree.relname_get(os.path.join(self.dirrelnamestack[-1],attrs["name"])))
    self.subobjstack.append([])

  def end_dir (self):
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    dir=Directory(self.dirleafnamestack.pop(),subobjs)
    dir.relname=self.dirrelnamestack.pop()
    self.subobjstack[-1].append(dir)

  def _doFile (self, attrs, fileCls):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      exit("Error in DirectoryTree: " + fileCls.TAG + " without name (attributes are " + unicode(attrs) + ")")
    assert isinstance(attrs["name"],unicode)
    file = fileCls(attrs["name"], WeakSignature.gen_dtml(attrs, fileCls), StrongSignature.gen_dtml(attrs, fileCls))
    file.relname=DirectoryTree.relname_get(os.path.join(self.dirrelnamestack[-1],attrs["name"]))
    self.subobjstack[-1].append(file)

  def do_file (self, attrs):
    self._doFile(attrs, RegularFile)

  def do_symlink (self,attrs):
    self._doFile(attrs, Symlink)

NONCHAR=unichr(0xFFFF)

class Object (object):
  def __init__ (self,leafname):
    if leafname==NONCHAR:
      exit("Error in Object: unable to support file or directory with name '"+leafname+"', which begins with U+FFFF")
    elif leafname==TMPDIR:
      exit("Error in Object: unable to support file or directory with name '"+leafname+"', because this clashes with the temporary directory name")
    self.leafname=leafname

  def __cmp__ (self,other):
    if not isinstance(other, Object):
      return NotImplemented
    return cmp(self.leafname,other.leafname)

  def writedtml (self,file,depth):
    raise NotImplementedError

class SentinelObject (object):
  def __init__ (self):
    self.leafname=NONCHAR

sentinelobj=SentinelObject()

class Directory (Object):
  def __init__ (self,leafname,subobjs):
    Object.__init__(self,leafname)
    #print "Creating Directory '"+unicode(leafname)+"'"
    self.subobjs=subobjs

  def writedtml (self,file,depth):
    file.write(u" "*depth)
    file.write(u"<DIR name=\"")
    file.write(cgi.escape(self.leafname,True))
    file.write(u"\">\n")
    for subobj in self.subobjs:
      subobj.writedtml(file,depth+2)
    file.write(u" "*depth)
    file.write(u"</DIR>\n")

class File (Object):
  @classmethod
  def stat (cls, pathname):
    raise NotImplementedError

  @classmethod
  def readBlocks (cls, pathname):
    raise NotImplementedError

  def __init__ (self,leafname,weakSignature,strongSignature):
    Object.__init__(self,leafname)
    #print "Creating File '"+unicode(leafname)+"'"
    assert weakSignature.fileCls is self.__class__
    self.weakSignature=weakSignature
    assert strongSignature.fileCls is self.__class__
    self.strongSignature=strongSignature

  def writedtml (self,file,depth):
    file.write(u" "*depth)
    file.write(u"<" + self.TAG + " name=\"")
    file.write(cgi.escape(self.leafname,True))
    file.write(u"\"")
    attrs={}
    self.weakSignature.getdtml(attrs)
    self.strongSignature.getdtml(attrs)
    for name in ("size", "sha512sum", "time"):
      file.write(u" "+name+"=")
      file.write(attrs[name])
    file.write(u">\n")

class RegularFile (File):
  @classmethod
  def stat (cls, pathname):
    return os.stat(pathname)

  @classmethod
  def readBlocks (cls, pathname):
    h = open(pathname, 'rb')
    while True:
      block = h.read(256*1024)
      if len(block) == 0:
        break
      yield block
    h.close()

  TAG = "FILE"

FS_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

def readlinkRaw (pathName):
  assert isinstance(pathName, unicode)
  body = os.readlink(pathName.encode(FS_ENCODING))
  assert isinstance(body, bytes)
  return body

class Symlink (File):
  @classmethod
  def stat (cls, pathname):
    return os.lstat(pathname)

  @classmethod
  def readBlocks (cls, pathname):
    yield readlinkRaw(pathname)

  TAG = "SYMLINK"

class WeakSignature (object):
  def __init__ (self, fileCls, size, lastModifiedTime):
    self.fileCls = fileCls
    self.size=int(size)
    if self.size<0:
      exit("Error in WeakSignature: initialised with size '"+unicode(size)+"', which is invalid")
    self.lastModifiedTime=int(lastModifiedTime)

  @staticmethod
  def gen_fs (pathname, fileCls):
    #print "Creating WeakSignature for '"+unicode(pathname)+"'"
    fileInfo = fileCls.stat(pathname)
    size=fileInfo.st_size
    #print "  size is "+unicode(size)
    lastModifiedTime=int(fileInfo.st_mtime*1000)
    #print "  lastModifiedTime is "+unicode(lastModifiedTime)
    return WeakSignature(fileCls, size, lastModifiedTime)

  @staticmethod
  def gen_dtml (attrs, fileCls):
    if not attrs.has_key("size") or not attrs.has_key("time"):
      exit("Error in WeakSignature.gen_dtml: size and time attributes both required")
    return WeakSignature(fileCls, attrs["size"], attrs["time"])

  def _eq (self, o):
    return self.fileCls is o.fileCls and self.size == o.size and self.lastModifiedTime == o.lastModifiedTime

  def __eq__ (self, o):
    if not isinstance(o, WeakSignature):
      return NotImplemented
    return self._eq(o)

  def __ne__ (self, o):
    if not isinstance(o, WeakSignature):
      return NotImplemented
    return not self._eq(o)

  def __hash__ (self):
    return (id(self.fileCls) ^ self.size ^ self.lastModifiedTime)

  def getdtml (self,attrs):
    attrs["size"]=unicode(self.size)
    attrs["time"]=unicode(self.lastModifiedTime)

OCTET_HEX_STRS = tuple(hex(b)[2:].zfill(2) for b in xrange(0, 256))

def renderHash (val):
  assert isinstance(val, str)
  assert len(val) == 64
  return u"".join(OCTET_HEX_STRS[ord(b)] for b in val)

def parseHash (val):
  assert isinstance(val, basestring)
  if len(val) != 128:
    exit("Error in StrongSignature.gen_dtml: sha512sum '" + val + "' invalid")
  try:
    return b"".join(chr(int(val[i:i + 2], 16)) for i in xrange(0, 128, 2))
  except ValueError:
    exit("Error in StrongSignature.gen_dtml: sha512sum '" + val + "' invalid")

class StrongSignature (object):
  def __init__ (self, fileCls, size, sha512sum):
    self.fileCls = fileCls
    self.size=int(size)
    if self.size<0:
      exit("Error in StrongSignature: initialised with size '"+unicode(size)+"', which is invalid")
    self.sha512sum = sha512sum

  @staticmethod
  def gen_fs (pathname, fileCls):
    size = fileCls.stat(pathname).st_size
    hashBuilder = hashlib.sha512()
    consumed=0
    for block in fileCls.readBlocks(pathname):
      consumed=consumed+len(block)
      hashBuilder.update(block)
    if consumed!=size:
      exit("Error while reading file for hashing: file '"+pathname+"' not properly read")
    return StrongSignature(fileCls, size, hashBuilder.digest())

  @staticmethod
  def gen_dtml (attrs, fileCls):
    if not attrs.has_key("size") or not attrs.has_key("sha512sum"):
      exit("Error in StrongSignature.gen_dtml: size and sha512sum attributes both required")
    return StrongSignature(fileCls, attrs["size"], parseHash(attrs["sha512sum"]))

  def _eq (self, o):
    return self.fileCls is o.fileCls and self.size == o.size and self.sha512sum == o.sha512sum

  def __eq__ (self, o):
    if not isinstance(o, StrongSignature):
      return NotImplemented
    return self._eq(o)

  def __ne__ (self, o):
    if not isinstance(o, StrongSignature):
      return NotImplemented
    return not self._eq(o)

  def __hash__ (self):
    return (id(self.fileCls) ^ self.size ^ hash(self.sha512sum))

  def getdtml (self,attrs):
    attrs["size"]=unicode(self.size)
    attrs["sha512sum"] = renderHash(self.sha512sum)

class DirectoryTreeDiffer (object):
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

class ScriptFile (object):
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

class BashScript (ScriptFile):
  def esc (s):
    return s.replace("\\","\\\\").replace("$","\\$").replace("`","\\`").replace("\"","\\\"")
  esc=staticmethod(esc)

  def winpathmap (path):
    if len(path)>1 and path[0].isalpha() and path[1]==":":
      path="/cygdrive/"+path[0].lower()+path[2:]
    return path.replace("\\","/")
  winpathmap=staticmethod(winpathmap)

  def __init__ (self,filename,forNow):
    self.file=codecs.open(filename+u".sh",'wb','utf-8')

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
    self.file.write("cp --no-dereference --preserve=all \"")
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

def pathSplit (path):
  r=[]
  pathSplitImpl(r,path)
  return r

def pathSplitImpl (out,path):
  (head,tail)=os.path.split(path)
  if not head or head == path:
    out.append(path)
  else:
    pathSplitImpl(out,head)
    out.append(tail)

class AbstractPythonScript (ScriptFile):
  def __init__ (self,filename,zipping):
    self.zipping=zipping
    self.file=open(filename+u".py",'wb')
    if zipping:
      head="""

import sys
import os
import os.path
import zipfile
import time

def mkdir (name):
  pass

FS_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

ALREADY_COMPRESSEDS = set(("zip", "tgz", "gz", "jpg", "png", "mp3", "flac", "oog", "avi", "mkv", "flv", "mov", "mp4", "m4a", "m4v"))

z = None

def startZip (p):
  global z
  z = zipfile.ZipFile(p, 'w', zipfile.ZIP_DEFLATED, True)

def endZip ():
  z.close()

def cp (src, dst):
  s = os.path.join(*src)
  if os.path.islink(s):
    st = os.lstat(s)
    # (see http://www.mail-archive.com/python-list@python.org/msg34223.html and zipfile.ZipFile.write())
    info = zipfile.ZipInfo("/".join(p for p in dst if p != os.curdir), time.localtime(st.st_mtime)[0:6])
    info.create_system = 3
    info.external_attr = (st.st_mode & 0xFFFF) << 16
    z.writestr(info, os.readlink(s.encode(FS_ENCODING)))
  else:
    mode = zipfile.ZIP_DEFLATED
    if os.path.splitext(src[-1])[1][1:].lower() in ALREADY_COMPRESSEDS:
      mode = zipfile.ZIP_STORED
    z.write(s, os.path.join(*dst), mode)

startZip("diffs.zip")

"""
      tail="""

endZip()

"""
    else:
      head="""

import sys
import os
import os.path
import shutil

FS_ENCODING = sys.getfilesystemencoding() or sys.getdefaultencoding()

def mkdir (name):
  p = os.path.join(*name)
  if not os.path.isdir(p):
    os.makedirs(p)

def rmdir (name):
  os.rmdir(os.path.join(*name))

def cp (src, dst):
  s = os.path.join(*src)
  d = os.path.join(*dst)
  if os.path.islink(s):
    os.symlink(os.readlink(s.encode(FS_ENCODING)), d)
  else:
    shutil.copy2(s, d)

def mv (src, dst):
  s = os.path.join(*src)
  d = os.path.join(*dst)
  if os.path.islink(s):
    os.symlink(os.readlink(s.encode(FS_ENCODING)), d)
    os.remove(s)
  else:
    shutil.move(s, d)

def rm (name):
  os.remove(os.path.join(*name))

"""
      tail=None
    self.file.write(head.strip() + "\n\n")
    self.tail=tail

  def comment (self,body):
    self.file.write("# ")
    self.file.write(body)
    self.file.write("\n")

  def writeCmd (self,fnName,*params):
    self.file.write(fnName)
    self.file.write("(")
    first=True
    for param in params:
      if not first:
        self.file.write(", ")
      first=False
      self.file.write(repr(tuple(pathSplit(param))))
    self.file.write(")\n")

  def mkdir (self,name):
    self.writeCmd("mkdir",name)

  def rmdir (self,name):
    assert not self.zipping
    self.writeCmd("rmdir",name)

  def cp (self,src,dst):
    self.writeCmd("cp",src,dst)

  def mv (self,src,dst):
    assert not self.zipping
    self.writeCmd("mv",src,dst)

  def rm (self,name):
    assert not self.zipping
    self.writeCmd("rm",name)

  def close (self):
    if self.tail:
      self.file.write("\n" + self.tail.strip())
    self.file.close()

class ZippingPythonScript (AbstractPythonScript):
  def __init__ (self,filename,forNow):
    AbstractPythonScript.__init__(self,filename,forNow)

class FilingPythonScript (AbstractPythonScript):
  def __init__ (self,filename,forNow):
    AbstractPythonScript.__init__(self,filename,False)

class ScriptDirectoryTreeDiffer (DirectoryTreeDiffer):
  class Files:
    def __init__ (self):
      self.oldfiles={}
      self.newfiles={}

  def diff (self,oldtree,newtree,new_pathname,output_pathname,scripttypeCls):
    self.new_pathname=new_pathname

    name=os.path.join(output_pathname,u"!builddiffs")
    self.builddiffs_file=scripttypeCls(name,True)
    self.builddiffs_file.comment("Copies files to be backed up to the current directory")
    name=os.path.join(output_pathname,u"!pre_applydiffs")
    self.preapplydiffs_file=scripttypeCls(name,False)
    self.preapplydiffs_file.comment("Prepares the previous state of the backup set, rooted in the current directory, for having the updated files copied over it")
    name=os.path.join(output_pathname,u"!post_applydiffs")
    self.postapplydiffs_file=scripttypeCls(name,False)
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
    self.builddiffs_file.comment("Diff set file count: "+unicode(self.builddiffs_files_count))
    self.builddiffs_file.comment("Diff set total bytes: "+unicode(self.builddiffs_files_size))

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
          if tmpdir is None:
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
    if olddir.tmpdir is not None:
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
    if obj is None:
      # The new file is not a direct copy of an old one
      obj=files.newfiles.get(newobj.strongSignature,None)
    if obj is not None:
      # The new file is a copy of an old one or another new one
      obj.copies.append(newobj)
    else:
      # The new file is neither a direct copy of an old one nor of a new one
      if not newdir.__dict__.has_key('inbuilddiffs'):
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
