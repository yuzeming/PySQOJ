#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import pdb
from time import sleep
import win32api
import win32event
import win32file
import win32pipe
import win32process
import pywintypes
import win32con
import win32security

WIN32_PROCESS_TIMES_TICKS_PER_SECOND = 1e7

ExeExt=".exe"

_sa= win32security.SECURITY_ATTRIBUTES ()
_sa.bInheritHandle=True

def CloseProcess(pi=None):
    if pi is not None:
        #pi  (hProcess, hThread, dwProcessId, dwThreadId)
        try:
            win32process.TerminateProcess(pi[0], 1)
        except pywintypes.error:
            pass
        win32event.WaitForSingleObject(pi[0], win32event.INFINITE)
        win32api.CloseHandle(pi[0])


def Exec(argv,limit=None,pp=None,RootDir=None):
    ret=[False,None,None,None]
    si= win32process.GetStartupInfo()
    if pp:
        si.hStdInput=pp[0]
        si.hStdOutput=pp[1]
        si.hStdError=pp[2]

    si.wShowWindow=win32con.SW_HIDE
    si.dwFlags = win32process.STARTF_USESHOWWINDOW | win32con.STARTF_USESTDHANDLES
    cmd=" ".join(argv)
    win32api.SetLastError(0)
    #PyHANDLE, PyHANDLE, int, int = CreateProcess(appName, commandLine , processAttributes , threadAttributes , bInheritHandles , dwCreationFlags , newEnvironment , currentDirectory , startupinfo )
    try:
        pi= win32process.CreateProcess(None,cmd,None,None,True,win32con.CREATE_SUSPENDED,None,RootDir,si)
    except pywintypes.error , e:
        ret[1]=e[2]
        return ret
    #pi  (hProcess, hThread, dwProcessId, dwThreadId)
    win32process.ResumeThread(pi[1]) #hThread
    win32api.CloseHandle(pi[1])

    while True:
        exitCode=win32process.GetExitCodeProcess(pi[0])
        pmc=win32process.GetProcessMemoryInfo(pi[0])
        ft=win32process.GetProcessTimes(pi[0])
        ret[3]=mem = round(float(pmc["PeakPagefileUsage"]) / 1024 / 1024,2)
        ret[2]=time= round(float(ft["UserTime"]) / WIN32_PROCESS_TIMES_TICKS_PER_SECOND,2)
        print exitCode,ret
        if limit is not None and time>limit[0]:
            ret[1]=u"超过时间限制"
            CloseProcess(pi)
            return ret
        if limit is not None and mem>limit[1]:
            ret[1]=u"超过内存限制"
            CloseProcess(pi)
            return ret
        if exitCode != 259:
            if not exitCode:
                ret[0]=True
            else:
                ret[1]=u"运行时错误"+unicode(exitCode)
            CloseProcess(pi)
            return ret
        sleep(0.05)

def CreatePipe():
    pp= win32pipe.CreatePipe(_sa,0)
    win32file.WriteFile(pp[1],"@")
    return pp

def CloseHandle(h):
    return win32api.CloseHandle(h)

def ReadPipe(pp,size=1024*4+1):
    CloseHandle(pp[1])
    ret=win32file.ReadFile(pp[0],size)
    CloseHandle(pp[0])
    return ret[1][1:]

def CopyFile(s,t):
    return win32api.CopyFile(s,t)

def DelFile(f):
    return win32api.DeleteFile(f)



