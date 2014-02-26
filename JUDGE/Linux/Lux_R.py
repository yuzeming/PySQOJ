#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import resource

Signal={

}

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

ExeExt=""

def Exec(argv,limit=None,pipe=None,RootDir=None):
    ret=[False,None,None,None]
    pid=os.fork()
    if pid==-1:
        return None
    if pid:
        #父进程
        state=os.wait4(pid,os.WUNTRACED)
        # 0	ru_utime	time in user mode (float)
        # 6	ru_minflt	page faults not requiring I/O
        ret[2:2]=[state[2][0],state[2][6]*resource.getpagesize()]
        if not os.WIFEXITED(state[1]):
            #运行时错误
            ret[1]=u"运行时错误"
            if (os.WIFSIGNALED(RunRet[1])) and Signal.has_key(os.WTERMSIG(RunRet[1])):
                ret[1]=Signal[os.WTERMSIG(RunRet[1])]
        else:
            ret[0]=True
        return ret
    else:
        #子进程
        #未在Cygwin中实现
        if limit is not None:
            resource.setrlimit(resource.RLIMIT_CPU,(limit[0],limit[0]))
            resource.setrlimit(resource.RLIMIT_AS,(limit[1]*1204*1024,limit[1]*1204*1024))
        if RootDir is not None:
            os.chdir(RootDir)
        if pipe is not None and len(pipe):
            for i in range(0,len(pipe)):
                if pipe[i] is not None:
                    os.dup2(pipe[i],i)
        #print "EXEC",argv
        os.execvp(argv[0],argv)
        exit(1)

def CloseHandle(fd):
    return os.close(fd)

def ReadPipe(pp,size=1024*4):
    CloseHandle(pp[1])
    Ret=os.read(pp[0],size)
    CloseHandle(pp[0])
    return Ret

def CreatePipe():
    return os.pipe()

def CopyFile(s,t):
    return os.link(s,t)

def DelFile(f):
    return os.unlink(f)