#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime
from tzinfo import utc
from django.dispatch import dispatcher
from django.db.models.signals import post_save
from settings import MEDIA_URL
import jsonfield
import pdb

class Problem(models.Model):
    Name = models.SlugField(verbose_name="编号",primary_key=True)
    Title= models.CharField(max_length=100,verbose_name="名称",null=True,blank=True)
    Data = models.FileField(upload_to="data",blank=True,null=True,verbose_name="数据")
    HTML = models.TextField(blank=True,verbose_name="题目")
    Solve = models.TextField(blank=True,verbose_name="题解")
    canSubmit=models.BooleanField(default=True,verbose_name="允许提交")
    isProbShow = models.BooleanField(default=True,verbose_name="允许查看题目")
    isDataShow = models.BooleanField(default=False,verbose_name="允许下载数据")
    isSolveShow = models.BooleanField(default=False,verbose_name="允许查看题解")
    Belg = models.ForeignKey("Contest",blank=True,null=True,related_name="Prob",on_delete=models.SET_NULL,verbose_name="加入比赛")
    Perm=None
    def InitPerm(self,user,ret=None):
        c=False
        self.Perm={
            "canEdit":user.is_superuser,
            "canDD":self.Data and (self.isDataShow or user.is_superuser ),
            "canViewProb":self.isProbShow or ( self.Belg and self.Belg.InitPerm(user,"CanViewProb") ) or user.is_superuser,
            "canSubmit":self.canSubmit or user.is_superuser,
            "canViewSolve":self.isSolveShow or user.is_superuser,
        }
        if self.Perm.has_key(ret):
            return self.Perm[ret]
   
    def __unicode__(self):
        return self.Name

class MadiaFile(models.Model):
    Name = models.SlugField(verbose_name="编号")
    Prob = models.ForeignKey(Problem,blank=True,null=True)
    File = models.FileField(upload_to="file",verbose_name="文件")
    FileName = models.CharField(max_length=200)
    Perm=None
    def InitPerm(self,user,ret=None,):
        if self.Prob:
            res=self.Prob.InitPerm(user,ret,)
            self.Perm=self.Prob.Perm
            return res
        return True

    def Url(self):
        return MEDIA_URL+str(self.pk)

    def __unicode__(self):
        return self.FileName

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    DefaultLang = models.CharField(max_length=20)
    ACTot = models.IntegerField(default=0)
    isAC = jsonfield.JSONField(default="{}")
    def UpDateSubmit(self,pname,isAC):
        if not self.isAC.has_key(pname):
            self.isAC[pname]=False
        self.isAC[pname]=isAC or self.isAC[pname]
        self.save()
    def InitPerm(self,user,**kwargs):
        self.Perm={
            "canSetPswd":user.is_superuser,
            "canChangePswd":user.is_authenticated() and user.pk==self.user.pk,
            "canDisableUser":user.is_superuser,
            "canDelUser":user.is_superuser,
        }
    def __unicode__(self):
        return self.user.username

class Contest(models.Model):
    Name = models.SlugField(verbose_name="编号",primary_key=True)
    Title = models.CharField(max_length=100,verbose_name="名称",null=True,blank=True)
    canRegister = models.BooleanField(default=True,verbose_name="允许用户注册")
    RegUser = models.ManyToManyField(User,related_name="join_contest",through="ResultData",verbose_name="注册用户",blank=True,null=True)
    Start = models.DateTimeField(verbose_name="开始时间")
    End = models.DateTimeField(verbose_name="结束时间")
    isShowRes = models.BooleanField(default=False,verbose_name="显示结果",help_text="允许用户在比赛结束前查看结果")
    
    def isEnd(self):
        return datetime.datetime.now(utc) >= self.End
    def isStart(self):
        return datetime.datetime.now(utc) >= self.Start
        
    Perm=None
    def InitPerm(self,user,ret=None):
        self.Perm={
            "hasReged":user in self.RegUser.all(),
            "canEdit":user.is_superuser,
            "canReg":self.canRegister and not self.isEnd() and not (user in self.RegUser.all()),
            "canViewRes":self.isShowRes or self.isEnd() or user.is_superuser,
            "canViewProb":self.isStart() or user.is_superuser,
            "canSubmit":self.isStart() and not self.isEnd() and (user in self.RegUser.all()),
            }
        if self.Perm.has_key(ret):
            return self.Perm[ret]
    def __unicode__(self):
        return self.Name
    
class Submit(models.Model):
    Data = models.DateTimeField(auto_now_add=True)
    User = models.ForeignKey(User)
    Prob = models.ForeignKey(Problem)
    Cont = models.ForeignKey(Contest,blank=True,null=True)
    Lang = models.CharField(max_length=20)
    isAC = models.BooleanField(default=False)
    isWait = models.BooleanField(default=True)
    Error = models.TextField()
    State = models.TextField(default="None")
    Src = models.IntegerField(default=0)
    File = models.FileField(upload_to="src")
    Detail = jsonfield.JSONField(default="[]") # list
    def __unicode__(self):
        return unicode(self.pk) + u"#" + unicode(self.User) + u"@" + unicode(self.Prob) + u":" + unicode(self.State)
    
    Perm=None
    def InitPerm(self,user,ret=None,**kwargs):
        self.Perm={
            "canViewState":self.Cont is None or self.Cont.InitPerm(user,"canViewRes") or user.is_superuser,
            "canViewFile":user.is_authenticated() and self.User.pk==user.pk or user.is_superuser,
            }
        if self.Perm.has_key(ret):
            return self.Perm[ret]
    
class ResultData(models.Model):
    User = models.ForeignKey(User)
    Contest = models.ForeignKey(Contest)
    Src = models.IntegerField(default=0)
    Result = jsonfield.JSONField(default="{}") # a map
    ResList=None
    def Update(self,spk,name,src,state):
        #pdb.set_trace()
        self.Result[name]=(spk,src,state)
        self.Src=0
        for x in self.Result:
            self.Src+=self.Result[x][1]
        print self.Result
        self.save()
    def GetResultList(self,ProbList):
        self.ResList=[]
        for x in ProbList:
            self.ResList.append(self.Result.get(x,None))
        return self.ResList
    def __unicode__(self):
        return unicode(self.User) + "@" +unicode(self.Contest) + ":" + unicode(self.Src)
    
    def InitPerm(self,user):
        pass

@dispatcher.receiver(post_save,sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    在新建用户时同时新建用户档案
    """
    if created:
        UserProfile.objects.create(user=instance)

from xmlRPCJudge import *

@dispatcher.receiver(post_save,sender=Submit)
def UpData_Submit(sender,instance,**kwargs):
    """
    更新用户数据
    """
    #pdb.set_trace()
    UserProfile.objects.get(user=instance.User).UpDateSubmit(instance.Prob.Name,instance.isAC)
    if instance.Cont:
        ResultData.objects.get(User=instance.User,Contest=instance.Cont).Update(instance.pk,instance.Prob.Name,instance.Src,instance.State)
    if instance.isWait:
        WakeupJudge()
    