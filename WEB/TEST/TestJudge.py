#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xmlrpclib
import copy
import shutil
import types
import time
import Conf
import json
import random
from Conf import JudgeKey

Server = xmlrpclib.ServerProxy(Conf.WebServer)
'''
ProbConf=[
    ["sum.in","sum.out"], #input,output
    ["Diff","%(OUT)","%(STD)","%(IN)"],#Compare
    [
        [10,["1.in","1.out",10,128],["2.in","2.out",10,128],["3.in","3.out",10,128]],#Sub1
        [10,["4.in","4.out",10,128],["5.in","5.out",10,128],["6.in","6.out",10,128]],#Sub2
    ],#DataConf
]
'''

'''
SubmitRes=[
    100,    # SID
    "",   # System Error
    [0,""], #CompileRet,CompileRes
    [10,False,#TotSrc,isAC,
    [
        [10,[1,"OK",2,123],[1,"OK",2,123],[1,"OK",2,123]],#Sub1
        [0,[1,"OK",2,123],[0,"BAD",2,123],[1,"OK",2,123]],#Sub2
    ]],#DataRes
]
'''

def Judge(s):
    DataRes=[random.randint(0,100),False,[]]
    if random.randint(0,10)==1:
        Ret= [s[0],u"系统错误",[0,""],None]
    elif random.randint(0,10)<3:
        Ret= [s[0],"",[1,u"编译错误"],None]
    else:
        Ret=[s[0],"",[0,u"测试"],None] # [SID,是否出错,编译结果,运行结果]
        DataRes[1]=bool(random.randint(0,3)==0)
        for i in range(10):
            subtask=[random.randint(0,10)]
            for x in range(3):
                subtask.append([random.randint(0,100)/100.0,"Random",random.randint(0,10),random.randint(0,512)])
            DataRes[2].append(subtask)
    Ret[3]=DataRes
    return Ret
    
def main():
    while True:
        s=Server.GetSubmit(JudgeKey)
        print s
        if s[0]==0:
            print "Wiat"
        else:
            Server.PostRes(JudgeKey,Judge(s))

if __name__ == '__main__':
    main()
