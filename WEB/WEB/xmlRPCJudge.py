#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
from WEB.md5file import MD5File
__author__ = 'YZM'
from models import *
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from settings import JudgeKey 
from settings import DataServer
from django.contrib import auth
from django.core.urlresolvers import reverse
from threading import Event
from django.core.files.base import ContentFile

Wakeup = Event()

def NewSubmit(prob,cont,lang,user_,src):
    submit=Submit()
    submit.Prob=prob
    submit.Lang=lang
    submit.User=user_
    submit.State=u"等待"
    submit.Cont=cont
    submit.save()
    submit.File.save(str(submit.pk),ContentFile(src.encode('UTF-8')))
    return submit

def WakeupJudge():
    Wakeup.set()

def RPC_AddSubmit(username,password,cont,prob,lang,src):
    """
    添加一个提交
    """
    user=auth.authenticate(username=username,password=password)
    if user is None:
        return False,"Login Fail"
    try:
        language=Language.objects.get(Name=lang)
        if cont:
            contest=Contest.objects.get(Name=cont)
            if not contest.InitPerm(user,"canSubmit"):
                return False,"Forbidden"
            problem=contest.Prob.get(Name=prob)
        else:
            contest=None
            problem=Problem.objects.get(Name=prob)
            if not problem.InitPerm(user,"canSubmit"):
                return False,"Forbidden"
    except Language.DoesNotExist:
        return False,"Language Error"
    except Contest.DoesNotExist:
        return False,"Contest Error"
    except Problem.DoesNotExist:
        return False,"Problem Error"
    submit=NewSubmit(problem,contest,language,user,src)
    return True,submit.pk

def RPC_GetSubmit(jk):
    if jk!=JudgeKey :
        return [-1]
    print "GetSubmit"
    submit = Submit.objects.filter(isWait=True)
    if not submit.exists():
        Wakeup.wait(30)
        return [0]
    Wakeup.clear()
    submit=submit[0]
    submit.State=u"评测中"
    submit.isWait=False
    submit.save()
    ret=[submit.pk,submit.Prob,submit.Lang,submit.File.read()]
    return ret

def RPC_PostRes(jk ,JudgeRes):
    print "PostRes",JudgeRes[0]
    if jk!=JudgeKey :
        return False
    try:
        submit = Submit.objects.get(pk=JudgeRes[0])
    except Submit.DoesNotExist:
        return False
    submit.Src=0
    if JudgeRes[1]:
        submit.State=submit.Error=u"系统错误"
    elif not JudgeRes[2][0]:
        submit.State=submit.Error=u"编译失败"
    else:
        submit.isAC=JudgeRes[3][1]
        if submit.isAC:
            submit.State=u"Accepted"
        else:
            submit.State=unicode(JudgeRes[3][0])
        submit.Src=JudgeRes[3][0]
    submit.Detail=JudgeRes
    submit.isWait=False
    submit.save()
    return True

def RPC_GetDataURL(jk ,name):
    if jk!=JudgeKey :
        return False
    try:
        Prob=Problem.objects.get(Name=name)
    except Problem.DoesNotExist:
        return False
    if not Prob.Data:
        return False
    return [MD5File(Prob.Data), DataServer + reverse("DataDownland",kwargs={"name":name}) + "?JudgeKey=" + JudgeKey]

XmlRPC = SimpleXMLRPCDispatcher(allow_none=True)
XmlRPC.register_function(RPC_GetSubmit,"GetSubmit")
XmlRPC.register_function(RPC_PostRes,"PostRes")
XmlRPC.register_function(RPC_AddSubmit,"AddSubmit")
XmlRPC.register_function(RPC_GetDataURL,"GetDataURL")
