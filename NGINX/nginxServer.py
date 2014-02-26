#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import win32serviceutil
import win32process
import win32service

ROOTDIR=r"D:\PySQOJ\NGINX"

class nginxServer(win32serviceutil.ServiceFramework):
    _svc_name_ = "PySQOJ_nginx"
    _svc_display_name_ = "PySQOJ Nginx Server"
    def SvcDoRun(self):
        os.chdir(ROOTDIR)
        os.system(os.path.join(ROOTDIR,"nginx.exe"))
    def SvcStop(self):
        os.chdir(ROOTDIR)
        os.system(os.path.join(ROOTDIR,"nginx.exe")+" -s quit")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(nginxServer)
