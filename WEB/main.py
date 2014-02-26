#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.core.servers.fastcgi import  runfastcgi
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WEB.settings")

def Main():
    runfastcgi(host="127.0.0.1",port="1879",method="threaded",maxchildren=20,daemonize="True")
    
if __name__ == '__main__':
    Main()
