#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xmlrpclib
import os
import sys
import copy
import shutil
import types
import time
import Conf
import json
from random import *

Server = xmlrpclib.ServerProxy(Conf.WebServer)

ContSet=["contest"]
ProbSet=["p0","p1","p2","p3","p4"]
LangSet=["cpp","pas"]
UserSet=[]
for i in range(10):
    UserSet.append(["U"+str(i),"password"])

def main():
    for i in range(100):
        cont=choice(ContSet)
        prob=choice(ProbSet)
        lang=choice(LangSet)
        user=choice(UserSet)
        src="test"
        #AddSubmit(username,password,cont,prob,lang,src)
        Server.AddSubmit(user[0],user[1],cont,prob,lang,src)

if __name__ == '__main__':
    main()
