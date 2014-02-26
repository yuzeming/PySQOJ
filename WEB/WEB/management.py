#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.dispatch import dispatcher 
from django.db.models.signals import post_syncdb

from WEB import models as WEB_app
import random
import datetime
from tzinfo import utc

DEBUG=False

@dispatcher.receiver(post_syncdb,sender=WEB_app)
def Init_User(**kwargs):
    """
    初始化超级管理员
    """
    WEB_app.User.objects.create_superuser("yzm","yuzeming@gmail.com","root")
    # 测试。添加10个测试用户
    if DEBUG:
        for i in range(10):
            WEB_app.User.objects.create_user("U"+str(i),"t@t.cn","password")

@dispatcher.receiver(post_syncdb,sender=WEB_app)
def Init_Language(**kwargs):
    """
    初始化语言
    """
    WEB_app.Language.objects.create(Name="c",FullName="Gun GCC")
    WEB_app.Language.objects.create(Name="cpp",FullName="Gun G++")
    WEB_app.Language.objects.create(Name="pas",FullName="Free Pascal")
    

@dispatcher.receiver(post_syncdb,sender=WEB_app)
def Init_Prob(**kwargs):
    """
    添加测试用的题目
    """
    if DEBUG:
        for i in range(100):
            prob=WEB_app.Problem()
            prob.Title=prob.Name="p"+str(i)
            prob.isShow=True
            prob.canDownlandData=False
            prob.HTML=r"<h1>test</h1>"
            prob.save()
    
@dispatcher.receiver(post_syncdb,sender=WEB_app)
def Init_Cont(**kwargs):
    """
    添加测试用的比赛
    """
    if DEBUG:
        for i in range(10):
            cont=WEB_app.Contest()
            cont.Title=cont.Name="c"+str(i)
            cont.canRegister=True
            cont.Start=datetime.datetime.now(utc)
            cont.End=datetime.datetime.now(utc)+ datetime.timedelta(hours=2)
            cont.save()
            for p in random.sample(WEB_app.Problem.objects.all(),5):
                cont.Prob.add(p)
        cont=WEB_app.Contest()
        cont.Title=cont.Name="contest"
        cont.canRegister=True
        cont.Start=datetime.datetime.now(utc)
        cont.End=datetime.datetime.now(utc) + datetime.timedelta(hours=2)
        cont.save()    
        for p in ("p0","p1","p2","p3","p4"):
            cont.Prob.add(WEB_app.Problem.objects.get(Name=p))
        for u in WEB_app.User.objects.all():
            WEB_app.ResultData.objects.create(Contest=cont,User=u,Src=0)
    