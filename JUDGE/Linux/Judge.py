#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from string import strip
import sys
import pdb
import copy
import types
from Conf import *
import json
import urllib
import zipfile
from xmlrpclib import ServerProxy
from  Win_R import *
from md5file import *
Web = ServerProxy(WebServer)

#CompileConf={
#        "cpp":["g++ $(SRC) -O2 -o $(EXE)","$(EXE)","cpp"],
#        "pas":["fpc $(SRC) -O2 -o $(EXE)","$(EXE)","pas"],
#    }

#ProbConf=[
#    ["sum.in","sum.out"], #input,output
#    ["Diff","%(OUT)","%(ANS)","%(IN)"],#Compare
#    [
#        [10,["1.in","1.out",10,128],["2.in","2.out",10,128],["3.in","3.out",10,128]],#Sub1
#        [10,["4.in","4.out",10,128],["5.in","5.out",10,128],["6.in","6.out",10,128]],#Sub2
#    ],#DataConf
#]
#SubmitRes=[
#    100,    # SID
#    None,   # System Error
#    [0,""], #CompileRet,CompileRes
#    [10,False,#TotSrc,isAC,
#    [
#        [10,[1,"OK",2,123],[1,"OK",2,123],[1,"OK",2,123]],#Sub1
#        [0,[1,"OK",2,123],[0,"BAD",2,123],[1,"OK",2,123]],#Sub2
#    ]],#DataRes
#]

def GetConf(name):
    """
    读取name文件中的json
    """
    try:
        ret=json.loads(file(name).read())
    except ValueError:
        ret=None
    return ret

def SaveToFile(text,name):
    f=open(name,"w")
    f.write(text)
    f.close()

def Split(s):
    if type(s)==types.StringType:
        return s.split(" ")
    else:
        return copy.deepcopy(s)

def Replace(L,M):
    for i in range(len(L)):
        if M.has_key(L[i]):
            L[i]=M[L[i]]

def Compile(Src,Exe,conf):
    conf=Split(conf)
    Replace(conf,{"$(SRC)":Src,"$(EXE)":Exe})
    pp=CreatePipe()
    Ret=Exec(conf,CompileLimits,[None,pp[1],pp[1]])
    return [Ret[0],ReadPipe(pp)]

def GetData(name,dir):
    f=os.path.join(DataDir,name+".zip")
    md5fn=os.path.join(DataDir,name+".md5")
    if os.path.exists(md5fn):
        fmd5=file(md5fn).read()
    else:
        fmd5=""
    tmp=Web.GetDataURL(JudgeKey,name)
    if not tmp:
        return False
    else:
        md5=tmp[0]
        url=tmp[1]
    if fmd5!=md5:
        try:
            urllib.urlretrieve (url, f)
        except IOError:
            return False
        fmd5=MD5File(open(f,"rb"))
        if fmd5!=md5:
            return False
        SaveToFile(fmd5,md5fn)
        if os.path.exists(dir):
            os.rmdir(dir)
        os.mkdir(dir)
        zipFile=zipfile.ZipFile(f)
        zipFile.extractall(dir)
        zipFile.close()
        mk=os.path.join(dir,"Makefile")
        if os.path.exists(mk):
            e= Exec(["make"],RootDir=dir)
            if not e[0]:
                return False
    return True

def Judge(s):
    """
    评测主函数
    参数
    s=[SubmitID,ProbID,Lang,Src]
    返回值
    [SubmitID,是否出错,编译结果,运行结果]
    """
    Ret=[s[0],False,False,False] # [SID,是否出错,编译结果,运行结果]
    #try:
    DataRoot=os.path.join(DataDir,str(s[1]))
    DataConfFile=os.path.join(DataRoot,"Conf.json")
    if not GetData(s[1],DataRoot):
        Ret[1]=u"数据未找到"
    ProbConf=GetConf(DataConfFile)
    if ProbConf is None:
        Ret[1]=u"数据配置无法读取"
    if Ret[1]:
        return Ret
    Src=os.path.join(SrcDir,str(s[0])+"."+CompileConf[s[2]][2])
    Exe=os.path.join(TempDir,str(s[0])) + ExeExt

    SaveToFile(s[3],Src)

    Ret[2]=Compile(Src,Exe,CompileConf[s[2]][0])
    if not Ret[2][0]:
        return Ret

    RunCmd=Split(CompileConf[s[2]][1])
    Replace(RunCmd,{"$(EXE)":Exe})
    if ProbConf[1] is None:
        CompareConf=Split(DefaultCompareConf)
    else:
        CompareConf=Split(ProbConf[1])
    if os.path.exists(os.path.join(DataRoot,CompareConf[0])):
        CompareConf[0]=os.path.join(DataRoot,CompareConf[0])
    else:
        CompareConf[0]=os.path.join(ComparerDir,CompareConf[0])
    InputFileName=os.path.join(TempDir,ProbConf[0][0])
    OutputFileName=os.path.join(TempDir,ProbConf[0][1])
    DataConf=ProbConf[2]

    Ret[3]=[0,True]
    for SubTask in DataConf:
        SubTaskRes=[SubTask[0],]
        for Data in SubTask[1:]:
            Input=os.path.join(DataRoot,Data[0])
            Output=os.path.join(DataRoot,Data[1])

            Limit=Data[2:4]
            if os.path.exists(InputFileName):
                DelFile(InputFileName)
            CopyFile(Input,InputFileName)

            DataRes=Exec(RunCmd,Limit,None,TempDir)
            if (DataRes[0]):
                #运行比较器
                DataRes[0]=0
                if not os.path.exists(OutputFileName):
                    DataRes[0:2]=[0,"Output Not Exists"]
                else:
                    tmpCC=copy.deepcopy(CompareConf)
                    Replace(tmpCC,{"$(IN)":Input,"$(OUT)":OutputFileName,"$(ANS)":Output,})
                    pp=CreatePipe() # (read_end,write_end)
                    CRet=Exec(tmpCC,pp=[None,pp[1],None])
                    CRes=ReadPipe(pp)
                    DataRes[0:2]=[0,"Compare Error"]
                    if CRet[0]:
                        tmpList=CRes.split(" ",1)
                        tmpList[0]=float(tmpList[0])
                        if 0<= tmpList[0] <= 1:
                            DataRes[0]=tmpList[0]
                            DataRes[1]=strip(tmpList[1])
                            if DataRes[1]=="":
                                if DataRes[0]==1:
                                    DataRes[1]="正确"
                                elif DataRes[0]==0:
                                    DataRes[1]="错误"
                                else:
                                    DataRes[1]="部分正确"
                            Ret[3][1]=Ret[3][1] and (DataRes[0]==1) # Set isAC
            else:
                DataRes[0]=0
            #Clean up
            DelFile(InputFileName)
            DelFile(OutputFileName)
            SubTaskRes.append(DataRes)
            SubTaskRes[0]=min(SubTaskRes[0],SubTask[0]*DataRes[0])
        Ret[3][0]+=SubTaskRes[0]
        Ret[3].append(SubTaskRes)
    DelFile(Exe)
    #except :
    #    Ret[1]="系统错误"
    return Ret

def Main():
    """
    主程序
    """
    while True:
    #    try:
        print "Try GetSubmit"
        s=Web.GetSubmit(JudgeKey)
        if s[0]>0:
            Web.PostRes(JudgeKey,Judge(s))
        elif s[0]<0:
            raise
    #    except :
    #        print sys.exc_info()
    #        sys.exc_clear()
    #        sleep(10)

if __name__ == '__main__':
    Main()

