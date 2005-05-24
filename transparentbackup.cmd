@setlocal enableextensions & I:\Apps\PROGRA~1\PYTHON~1.4\python.exe -x "%~f0" "%*" & goto :EOF
#  -------------------------------------------------------------------
#  Transparent Backup V1.00                       PYTHON COMPONENTS
#  © Geoff Crossland 2005
#
#  V1.00 : Compares a directory tree with a DTML file and creates
#          data about the differences between them.
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



def main (args):
  syntax="Syntax: transparentbackup [-b|--backup-source <backupdir>] [-d|--diff-dtml <dtmlfile>] [-o|--output <outputdir>]"
  (optlist,leftargs)=getopt.getopt(args,"b:d:o:",["backup-source=","diff-dtml=","output="])
  if len(leftargs)>0:
    sys.exit("Unknown arguments on command line ('"+leftargs+"')\n"+syntax)
  opt_backup_source=None
  opt_diff_dtml=None
  opt_output=None
  for (option,value) in optlist:
    if option in ("-b","--backup-source"):
      opt_backup_source=value
    if option in ("-d","--diff-dtml"):
      opt_diff_dtml=value
    if option in ("-o","--output"):
      opt_output=value
  if opt_backup_source==None:
    sys.exit("No backup source path (-b) supplied\n"+syntax)
  if not os.path.isdir(opt_backup_source):
    sys.exit("Backup source path (-b) is not a directory\n"+syntax)
  if opt_output==None:
    sys.exit("No output path (-o) supplied\n"+syntax)
  if not os.path.isdir(opt_output):
    sys.exit("Output path (-b) is not a directory\n"+syntax)
  opt_backup_source=os.path.abspath(opt_backup_source)
  if opt_diff_dtml!=None:
    opt_diff_dtml=os.path.abspath(opt_diff_dtml)

  print "Backup source: "+opt_backup_source
  print "DTML file: "+str(opt_diff_dtml)
  opt_output=os.path.abspath(opt_output)
  print "Output: "+opt_output

  transparentbackup(opt_backup_source,opt_diff_dtml,opt_output)



def transparentbackup (new_pathname,old_dtml,output_pathname):
  if old_dtml==None:
    oldtree=DirectoryTree.gen_empty()
  else:
    oldtree=DirectoryTree.gen_dtml(old_dtml)
  newtree=DirectoryTree.gen_fs(new_pathname)
  DirectoryTreeDiffer().diff(oldtree,newtree,new_pathname,output_pathname)
  newtree.writedtml(os.path.join(output_pathname,"!fullstate.dtml"))



class DirectoryTree:
  def __init__ (self,root):
    self.root=root

  def gen_empty ():
    return DirectoryTree(Directory(None,[]))
  gen_empty=staticmethod(gen_empty)

  def gen_fs (source_pathname):
    (t,source_leafname)=os.path.split(source_pathname)
    if len(source_leafname)==0:
      sys.exit("Error while reading backup source: the pathname appears to have a directory seperator on the end (if refering to a directory, omit this)")
    return DirectoryTree(DirectoryTree.gen_fs_dir(None,source_pathname))
  gen_fs=staticmethod(gen_fs)

  def gen_fs_dir (source_leafname,source_pathname):
    subobjs=[]
    subobjs=os.listdir(source_pathname)
    subobjs.sort()
    i=0
    while i<len(subobjs):
      leafname=subobjs[i]
      pathname=os.path.join(source_pathname,leafname)
      if os.path.isdir(pathname):
        subobjs[i]=DirectoryTree.gen_fs_dir(leafname,pathname)
      else:
        subobjs[i]=File(leafname,Signature.gen_fs(pathname))
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
    self.dirnamestack=[]
    self.subobjstack=[]

    file=open(pathname,"rb")
    data=file.read()
    file.close()

    self.subobjstack.append([])

    self.feed(data)
    self.close()

    if len(self.subobjstack)!=1:
      sys.exit("Error in DirectoryTree: while parsing a DTML file, found that DIR tags had not been closed")
    assert len(self.dirnamestack)==0
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    self.root=Directory(None,subobjs)

  def report_unbalanced (self,tag):
    sys.exit("Error in DirectoryTree: while parsing a DTML file, found an end '"+tag+"' tag without a start tag")

  def start_dir (self,attrs):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      sys.exit("Error in DirectoryTree: DIR without name (attributes are "+str(attrs)+")")
    self.dirnamestack.append(attrs["name"])
    self.subobjstack.append([])

  def end_dir (self):
    subobjs=self.subobjstack.pop()
    subobjs.sort()
    self.subobjstack[-1].append(Directory(self.dirnamestack.pop(),subobjs))

  def do_file (self,attrs):
    attrs=DirectoryTree_DTMLParser.processattrs(attrs)
    if not attrs.has_key("name"):
      sys.exit("Error in DirectoryTree: FILE without name (attributes are "+str(attrs)+")")
    self.subobjstack[-1].append(File(attrs["name"],Signature.gen_dtml(attrs)))



class Object:
  def __init__ (self,leafname):
    if leafname!=None and len(leafname)>0 and leafname[0]==chr(255):
      sys.exit("Error in Object: unable to support file or directory with name '"+leafname+"', which begins with chr(255)")
    self.leafname=leafname

  def __cmp__ (self,other):
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
  def __init__ (self,leafname,signature):
    Object.__init__(self,leafname)
    self.signature=signature

  def writedtml (self,file,depth):
    file.write(" "*depth)
#   file.write("<FILE name=")
#   file.write(xml.sax.saxutils.quoteattr(self.leafname))
    file.write("<FILE name=\"")
    file.write(cgi.escape(self.leafname,True))
    file.write("\" ")
    self.signature.writedtml(file)
    file.write(">\n")



class Signature:
  def __init__ (self,size,md5sum_hexstring):
    if len(md5sum_hexstring)!=32:
      sys.exit("Error in Signature: initialised with MD5 sum '"+md5sum_hexstring+"', which is invalid")
    self.size=int(size)
    self.md5sum=md5sum_hexstring.upper()

  def gen_fs (pathname):
    size=os.stat(pathname).st_size
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
    return Signature(size,md5sum.hexdigest())
  gen_fs=staticmethod(gen_fs)

  def gen_dtml (attrs):
    if not attrs.has_key("size") or not attrs.has_key("md5sum"):
      sys.exit("Error in Signature.gen_dtml: size and md5sum attributes both required")
    return Signature(attrs["size"],attrs["md5sum"])
  gen_dtml=staticmethod(gen_dtml)

  def __cmp__ (self,other):
    #print "    __cmp__ing:"
    #print "      "+str(self.size)+","+str(self.md5sum)
    #print "      "+str(other.size)+","+str(other.md5sum)

    if self.size<other.size:
      #print "      self less size"
      return -1
    #print "again, self size is "+str(self.size)+" and other size is "+str(other.size)
    if self.size>other.size:
      return 1
    if self.md5sum<other.md5sum:
      #print "      self less sum"
      return -1
    if self.md5sum>other.md5sum:
      #print "      self more sum"
      return 1
    #print "      self same"
    return 0

  def __hash__ (self):
    return (self.size^self.md5sum.__hash__())

  def writedtml (self,file):
    file.write("size=")
    file.write(str(self.size))
    file.write(" md5sum=")
    file.write(str(self.md5sum))



class DirectoryTreeDiffer:
  def diff (self,oldtree,newtree,new_pathname,output_pathname):
    self.new_pathname=new_pathname
#   self.output_pathname=output_pathname
    self.builddiffs_file=open(os.path.join(output_pathname,"!builddiffs.bat"),"wb")
    self.applydiffs_file=open(os.path.join(output_pathname,"!applydiffs.bat"),"wb")
    self.builddiffs_file.write("REM Copies files to be backed up to the current directory\n")
    self.applydiffs_file.write("REM Deletes files no longer present, rooted in the current directory\n")
    self.diff_dir(oldtree.root,newtree.root,".")
    self.builddiffs_file.close()
    self.applydiffs_file.close()

  def diff_dir (self,olddir,newdir,source_pathname):
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
    #print "file oldsubobjs is "+str(oldsubobjs)
    #print "file newsubobjs is "+str(newsubobjs)
    while old!=sentinelobj or new!=sentinelobj:
      if old.leafname==new.leafname:
        #print "Looking at "+old.leafname+" and its identically named companion:"
        #print "  Old size:"+str(old.signature.size)
        #print "  New size:"+str(new.signature.size)
        #print "  Old md5:"+str(old.signature.md5sum)
        #print "  New md5:"+str(new.signature.md5sum)
        # An old file still exists
        if old.signature!=new.signature:
          #print "  The sigs are different"
          self.file_modified(old,new,os.path.join(source_pathname,old.leafname))
        #else:
          #print "  The sigs are the same"
          self.file_unmodified(old,new,os.path.join(source_pathname,old.leafname))
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
        new=newsubobjs[newindex]
        newindex=newindex+1
      elif old.leafname<new.leafname:
        # An old file no longer exists
        self.file_del(old,os.path.join(source_pathname,old.leafname))
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
      else:
        # A new file has been created
        self.file_gen(new,os.path.join(source_pathname,new.leafname))
        new=newsubobjs[newindex]
        newindex=newindex+1

    # Then, process directories
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,Directory)]+[sentinelobj]
    old=oldsubobjs[0]
    oldindex=1
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,Directory)]+[sentinelobj]
    new=newsubobjs[0]
    newindex=1
    #print "dir oldsubobjs is "+str(oldsubobjs)
    #print "dir newsubobjs is "+str(newsubobjs)
    while old!=sentinelobj or new!=sentinelobj:
      if old.leafname==new.leafname:
        # An directory still exists
        t=os.path.join(source_pathname,old.leafname)
        self.dir_unmodified(old,new,t)
        self.diff_dir(old,new,t)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
        new=newsubobjs[newindex]
        newindex=newindex+1
      elif old.leafname<new.leafname:
        # An old directory no longer exists
        t=os.path.join(source_pathname,old.leafname)
        self.diff_dir_del(old,t)
        self.dir_del(old,t)
        old=oldsubobjs[oldindex]
        oldindex=oldindex+1
      else:
        # A new directory has been created
        t=os.path.join(source_pathname,new.leafname)
        self.dir_gen(new,t)
        self.diff_dir_gen(new,t)
        new=newsubobjs[newindex]
        newindex=newindex+1

  def diff_dir_gen (self,newdir,source_pathname):
    assert isinstance(newdir,Directory)

    # First, process files
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,File)]
    for new in newsubobjs:
      #print "Looking at file "+new.leafname+", in a directory being recursively created:"
      self.file_gen(new,os.path.join(source_pathname,new.leafname))

    # Then, process directories
    newsubobjs=[subobj for subobj in newdir.subobjs if isinstance(subobj,Directory)]
    for new in newsubobjs:
      #print "Looking at dir "+new.leafname+", in a directory being recursively created:"
      t=os.path.join(source_pathname,new.leafname)
      self.dir_gen(new,t)
      self.diff_dir_gen(new,t)

  def diff_dir_del (self,olddir,source_pathname):
    assert isinstance(olddir,Directory)

    # First, process files
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,File)]
    for old in oldsubobjs:
      #print "Looking at file "+old.leafname+", in a directory being recursively deleted:"
      self.file_del(old,os.path.join(source_pathname,old.leafname))

    # Then, process directories
    oldsubobjs=[subobj for subobj in olddir.subobjs if isinstance(subobj,Directory)]
    for old in oldsubobjs:
      #print "Looking at dir "+old.leafname+", in a directory being recursively deleted:"
      t=os.path.join(source_pathname,old.leafname)
      self.diff_dir_del(old,t)
      self.dir_del(old,t)

  def dir_gen (self,newobj,pathname):
    self.builddiffs_file.write("MKDIR \"")
    self.builddiffs_file.write(pathname)
    self.builddiffs_file.write("\"\n")

  def dir_del (self,oldobj,pathname):
    self.applydiffs_file.write("RMDIR \"")
    self.applydiffs_file.write(pathname)
    self.applydiffs_file.write("\"\n")

  def dir_unmodified (self,oldobj,newobj,pathname):
    self.dir_gen(newobj,pathname)

  def file_gen (self,newobj,pathname):
    self.builddiffs_file.write("COPY \"")
    self.builddiffs_file.write(os.path.join(self.new_pathname,pathname))
    self.builddiffs_file.write("\" \"")
    self.builddiffs_file.write(pathname)
    self.builddiffs_file.write("\"\n")

  def file_del (self,oldobj,pathname):
    self.applydiffs_file.write("DEL /F \"")
    self.applydiffs_file.write(pathname)
    self.applydiffs_file.write("\"\n")

  def file_modified (self,oldobj,newobj,pathname):
    self.file_gen(newobj,pathname)

  def file_unmodified (self,oldobj,newobj,pathname):
    pass



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
