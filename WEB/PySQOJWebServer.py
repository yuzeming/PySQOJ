#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import win32serviceutil
import main

class PySQOJWebServer(win32serviceutil.ServiceFramework):
    _svc_name_ = "PySQOJ_web"
    _svc_display_name_ = "PySQOJ Python FastCGI Server"
    def SvcDoRun(self):
        main.Main()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PySQOJWebServer)
