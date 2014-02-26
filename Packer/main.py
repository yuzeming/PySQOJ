#!/usr/bin/python
# -*- coding: UTF-8 -*-

#自动配置工具
#
#1.选择一个模板
#2.将$EXT 替换为*，搜索某一数据的文件列表，并构建树状结构
#3.某一数据的文件列表中，$NAME替换为*，搜索输入输出
#

import os
import sys
import fnmatch
import getopt
from string import Template
import math

EXEEXT = ".exe" if sys.platform in ("win32",'cygwin',) else ""
CMPER = ["cmp","check","diff","compare"]

INPUTEXT=["in","input","i"]
OUTPUTEXT=["out","output","o","ans","ok","res","sol"]

TEMPLATE=[
    "$NAME$I.$EXT",
    "$NAME.$I.$EXT",
    "$NAME.$EXT$I",
    "$NAME$I-$i.$EXT",
    "$EXT",
    "$EXT.txt",
]

I_LIST="0123456789abcdefghijklmnopqrstuvwxyz"

def GetFile(fn,ls):
    ret=[]
    for f in ls:
        if fnmatch.fnmatch(f,fn):
            ret.append(f)
    return ret

def AutoGenExt(template,dirlist,extlist):
    t=Template(template.copy())
    t.template=t.safe_substitute(NAME="*",I="*",i="*")
    for ext in extlist:
        for x in dirlist:
            if fnmatch.fnmatch(x,t.safe_substitute(EXT=ext)):
                return x
    return None

def AutoGen(template,dirlist,name,iex,oex):
    t=Template(template.copy())
    t.template=t.safe_substitute(NAME=name,EXT="*")
    ret=[]
    for I in I_LIST:
        xi=t.safe_substitute(i="x")==t.safe_substitute(i="o")
        subtask=[]
        for i in (I_LIST if xi else [""]):
            fn=t.safe_substitute(i=i)
            print fn
            filelist=GetFile(fn,dirlist)
            if not filelist:
                break
            inf=AutoGenExt(filelist,template,iex)
            otf=AutoGenExt(filelist,template,oex)
            if inf is None or otf is None:
                break
            subtask.extend([inf,otf])
        if len(subtask)==0:
            break
        ret.append(subtask)
    return ret

def AutoConf(Dir,time=1,mem=512,templist=None,name=None):
    Ret=[None,None,None]
    if name is None:
        name=os.path.dirname(Dir)
    Ret[0]=[name+".in",name+".out"] #input output name
    dirList=os.listdir(Dir)
    cmper=None
    for x in CMPER:
        if (x+EXEEXT) in dirList:
            cmper=x+EXEEXT

    Ret[1]=[cmper,"$IN","$OUT","$ANS"] # Compare Set

    DataConf = []

    for T in (TEMPLATE if templist is None else [templist]):
        DataConf=AutoGen(T,dirList,name,INPUTEXT,OUTPUTEXT)
        if DataConf:
            break

    if not DataConf:
        return False

    for st in DataConf:
        st.insert(0,round(100.0/len(FileSet),2))
        for p in st:
            p.extend([time,mem])

    Ret[2]=DataConf

    return Ret

def Main():
    if len(sys.argv)<2:
        usage(True)

    opts,args=None,None
    Dir=sys.argv[1]
    assert os.path.isdir(Dir) , "%s 不是目录" % Dir
    time=1
    men=512
    templist=None
    name=None
    pack=False
    showguo=False
    try:
        opts, args = getopt.getopt(sys.argv[2:], "hgpn:t:m:x:",["help","gui","pack","name=","time=","mem=","template="] )
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage(True)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage(True)
        elif o in ("-p", "--pack"):
            pack=True
        elif o in ("-t","--time"):
            try:
                time=float(a)
            except ValueError:
                assert False,"option %s is not a float" % o
        elif o in ("-m","--men"):

        else:
            assert False, "unhandled option"
            # ...

if __name__ == "__main__":
    Main()
