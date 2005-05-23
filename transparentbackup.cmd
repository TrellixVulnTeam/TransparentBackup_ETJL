@setlocal enableextensions & I:\Apps\PROGRA~1\PYTHON~1.4\python.exe -x "%~f0" "%*" & goto :EOF
#  -------------------------------------------------------------------
#  Transparent Backup V1.00                       PYTHON COMPONENTS
#  © Geoff Crossland 2005
#
#  V1.00 : Compares a directory tree with a DTML file and creates
#          data about the differences between them.
# -----------------------------------------------------------------  #
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
  if opt_diff_dtml==None:
    sys.exit("No DTML source file (-d) supplied\n"+syntax)
  if opt_output==None:
    sys.exit("No output path (-o) supplied\n"+syntax)
  if not os.path.isdir(opt_output):
    sys.exit("Output path (-b) is not a directory\n"+syntax)

  opt_backup_source=os.path.abspath(opt_backup_source)
  print "Backup source: "+opt_backup_source
  opt_diff_dtml=os.path.abspath(opt_diff_dtml)
  print "DTML file: "+opt_diff_dtml
  opt_output=os.path.abspath(opt_output)
  print "Output: "+opt_output

  transparentbackup(opt_backup_source,opt_diff_dtml,opt_output)



def transparentbackup (backup_source,diff_dtml,output):
  dirtree=DirectoryTree.gen_fs(backup_source)
  dirtree.writedtml(diff_dtml)
  dirtree=DirectoryTree.gen_dtml(diff_dtml)
  dirtree.writedtml("dump.dtml")



class DirectoryTree:
  def __init__ (self,root):
    self.root=root

  def gen_fs (source_pathname):
    (t,source_leafname)=os.path.split(source_pathname)
    if len(source_leafname)==0:
      sys.exit("Error while reading backup source: the pathname appears to have a directory seperator on the end (if refering to a directory, omit this)")
    return DirectoryTree(DirectoryTree.gen_fs_directory(None,source_pathname))
  gen_fs=staticmethod(gen_fs)

  def gen_fs_directory (source_leafname,source_pathname):
    subobjs=[]
    subobjs=os.listdir(source_pathname)
    subobjs.sort()
    i=0
    while i<len(subobjs):
      leafname=subobjs[i]
      pathname=os.path.join(source_pathname,leafname)
      if os.path.isdir(pathname):
        subobjs[i]=DirectoryTree.gen_fs_directory(leafname,pathname)
      else:
        subobjs[i]=File(leafname,Signature.gen_fs(pathname))
      i=i+1
    return Directory(source_leafname,subobjs)
  gen_fs_directory=staticmethod(gen_fs_directory)

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
    self.leafname=leafname

  def __cmp__ (self,other):
    if self.leafname<other.leafname:
      return -1
    if self.leafname>other.leafname:
      return 1
    return 0

  def writedtml (self,file,depth):
    raise NotImplementedError



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
    self.size=size
    self.md5sum=md5sum_hexstring.upper()

  def gen_fs (pathname):
    size=os.stat(pathname).st_size
    md5sum=md5.new()
    file=open(pathname,"rb")
    consumed=0
    while True:
      block=file.read(128*1024)
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

  def writedtml (self,file):
    file.write("size=")
    file.write(str(self.size))
    file.write(" md5sum=")
    file.write(str(self.md5sum))



if __name__=="__main__":
  argv=sys.argv
  if len(argv)<2:
    main([])
  elif len(argv)==2:
    main(string.split(argv[1]))
  else:
    main(argv[1:])
