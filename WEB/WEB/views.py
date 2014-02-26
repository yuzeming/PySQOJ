#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Create your views here.
import base64
from math import *
from models import *
from xmlRPCJudge import *
from django.http import *
from django.shortcuts import *
from django.core.files.base import ContentFile
from django.contrib import auth
from urllib import quote
from django.contrib.auth.views import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
import zipfile
from forms import *
import copy
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test,login_required
import pdb


PROB_PRE_PAGE=20
STATE_PRE_PAGE=40

def isAdmin(user):
    return user.is_superuser

def HttpResponseGo(request):
    try:
        href=request.META["HTTP_REFERER"]
    except KeyError:
        href="/"
    return HttpResponseRedirect(href)

def HttpResponseConfirm(request,list=[],title="确认"):
    q=request.GET.copy()
    q.setlist("confirm",["YES"])
    return render(request,"confirm.html",{"List":list,"href":request.path+"?"+q.urlencode(),"title":title})

def HttpResponseFileDownland(file,name=None,mimetype=None):
    wrapper=FileWrapper(file)
    response=HttpResponse(wrapper,mimetype=mimetype)
    if name:
        response['Content-Disposition'] = 'attachment; filename='+quote(name.encode('utf8'))
    return response

def IndexPage(request):
    """
    首页,什么都没有
    """
    if request.user.is_anonymous():
        messages.info(request,u"请登录，或者注册一个账户")
    return render(request,"index.html",locals())

def ShowList(request,templatename,QuerySets,**kwargs):
    """
    实现显示列表，分页
    """
    nowPage=int(request.GET.get("page","1"))
    totPage=int(ceil(QuerySets.count()/float(PROB_PRE_PAGE)))
    PageSet=range(max(1,nowPage-10),min(totPage,nowPage+10)+1)
    if (nowPage>totPage or nowPage<=0) and totPage!=0:
        raise Http404()
    Set=QuerySets.all()[(nowPage-1)*PROB_PRE_PAGE:nowPage*PROB_PRE_PAGE]
    for x in Set:
        x.InitPerm(request.user)
    dict_=locals()
    if kwargs:
        dict_.update(kwargs)
    return render(request,templatename,dict_)

def ProbListPage(request):
    """
    显示题目列表
    """
    return ShowList(request,"probList.html",Problem.objects,canEditProb=request.user.is_superuser)

def ProbSolvePage(request,name):
    Prob=get_object_or_404(Problem,Name=name)
    if not Prob.InitPerm(request.user,"canViewSolve"):
        messages.error(request,u"无权查看题解")
        return HttpResponseGo(request)
    return render(request,"solveShow.html",locals())

def ProbShowPage(request,name):
    """
    显示题目
    """
    Prob=get_object_or_404(Problem,Name=name)
    if not Prob.InitPerm(request.user,"canViewProb"):
        messages.error(request,u"无权查看题目")
        return HttpResponseGo(request)
    return render(request,"probShow.html",locals())

def ContListPage(request):
    """
    比赛列表
    """
    return ShowList(request,"contList.html",Contest.objects.order_by("-Start"),canEditCont=request.user.is_superuser)

def ContShowPage(request,name):
    """
    显示某场比赛的题目列表
    """
    cont=get_object_or_404(Contest,Name=name)
    if not cont.InitPerm(request.user,"canViewProb"):
        messages.error(request,u"您没有权限查看题目，请等待比赛开始")
        return HttpResponseGo(request)
    return ShowList(request,"probList.html",cont.Prob,cont=cont)

@login_required
def SubmitPage(request,cont=None):
    """
    提交页面
    """
    #pdb.set_trace()
    contest=None
    if cont:
        try:
            contest=Contest.objects.get(Name=cont)
        except Contest.DoesNotExist:
            raise Http404()
        if not contest.InitPerm(request.user,"canSubmit"):
            messages.error(request,u"不能提交该题,比赛已经结束,或者没有注册这场比赛")
            return HttpResponseGo(request)
    if request.method == 'POST':
        form=SubmitForm(request.POST)
        form.User=request.user
        if contest:
            form.ProbSet=contest.Prob
        if form.is_valid():
            submit=NewSubmit(form.cleaned_data["Prob"],contest,form.cleaned_data["Lang"],request.user,form.cleaned_data["File"])
            messages.success(request,u"成功提交")
            return HttpResponseRedirect(reverse("Detail",kwargs={"pk":str(submit.id)}))
    else:
        prob=request.GET.get("p","")
        form=SubmitForm(initial={"Prob":prob,"Lang":request.user.get_profile().DefaultLang})
    return render(request,"submit.html",locals())

def StatePage(request,action="show"):
    """
    显示运行状态
    """
    q=request.GET.copy()
    canRejudge=isAdmin(request.user)
    submit=None
    if q.get("s",False):
        try:
            submit=Submit.objects.filter(pk=q.get("s"))
        except Submit.DoesNotExist:
            messages.error(request,u"错误的提交ID")
    elif q.get("p",False):
        try:
            prob=Problem.objects.get(Name=q.get("p"))
        except Problem.DoesNotExist:
            messages.error(request,u"错误的题目名称")
        else:
            submit=Submit.objects.filter(Prob=prob)
    elif q.get("c",False):
        try:
            cont=Contest.objects.get(Name=q.get("c"))
        except Contest.DoesNotExist:
            messages.error(request,u"错误的比赛")
        else:
            submit=Submit.objects.filter(Cont=cont)
    else:
        submit=Submit.objects.all()
    if action=="rejudge":
        if not canRejudge:
            messages.error(request,"没有重新评测的权限")
        elif q.get("confirm","NO")=="YES":
            submit.update(isWait=True)
            WakeupJudge()
            messages.success(request,u"已经加入等待列表")
            return HttpResponseRedirect(reverse("State"))
        else:
            q.setlist("confirm",["YES"])
            return render(request,"confirm.html",{"List":submit,"href":request.path+"?"+q.urlencode(),"title":"确认重新评测"})
    return ShowList(request,"state.html",submit.order_by("-id"),canRejudge=canRejudge)

def DetailPage(request,pk):
    """
    显示评测详情
    """
    submit=get_object_or_404(Submit,pk=pk)
    submit.InitPerm(request.user)
    if submit.Detail:
        detail=copy.deepcopy(submit.Detail)
        if detail[3]:
            datares=detail[3][2:]
            for i in datares:
                for x in i[1:]:
                    x[1]=base64.decodestring(x[1])
        else:
            datares=None
    return render(request,"detail.html",locals())

def DataDownlandPage(request,name):
    """
    数据包下载
    """
    prob=get_object_or_404(Problem,Name=name)
    if (prob.InitPerm(request.user,"canDD") or request.GET.get("JudgeKey","") == JudgeKey) and prob.Data:
        return HttpResponseFileDownland(prob.Data,'%s-data.zip' % (name),"application/zip")
    else:
        messages.error(request,u"数据不提供下载或者您没有管理权限")
        return HttpResponseRedirect(reverse("ProbList"))

@user_passes_test(isAdmin)
def FileManagerPage(request,name=None):
    """
    显示文件列表
    """
    popup=bool(request.GET.get("popup",False))
    if name is None:
        messages.error(request,u"请指定绑定的题目")
        return HttpResponseGo(request)
    prob=get_object_or_404(Problem,Name=name)
    if request.GET.get("del",False):
        #Del A File
        pk=int(request.GET.get("del"))
        file=get_object_or_404(MadiaFile,pk=pk)
        if request.GET.get("confirm","NO")=="YES":
            tmp=unicode(file.File)
            file.File.delete()
            file.delete()
            messages.success(request,u"成功删除%s"%tmp)
            return HttpResponseRedirect(request.path)
        else:
            return HttpResponseConfirm(request,[file],title="确认删除以下文件")
    else:
        files=MadiaFile.objects.filter(Prob=prob)
        if popup:
            return ShowList(request,"filemanager_popup.html",files,prob=prob)
        else:
            return ShowList(request,"filemanager.html",files,prob=prob)

@user_passes_test(isAdmin)
def AddFilePage(request,name=None):
    """
    上传一个文件
    """
    if name is None:
        messages.error(request,u"请指定绑定的题目")
        return HttpResponseGo(request)
    prob=get_object_or_404(Problem,Name=name)
    if request.method=="POST":
        for f in request.FILES:
            tmp=MadiaFile()
            tmp.Prob=prob
            tmp.FileName=request.FILES[f].name
            tmp.save()
            tmp.File.save(prob.Name+"_"+request.FILES[f].name,request.FILES[f],save=True)
            messages.success(request,u"成功上传%s" % request.FILES[f].name)
        return HttpResponseRedirect(reverse("FileManager",kwargs={"name":prob.Name}))
    else:
        return render(request,'upland.html',locals())

def LoadHTML(prob):
    try:
        zipf=zipfile.ZipFile(prob.Data)
    except zipfile.BadZipfile:
        prob.Data.delete()
        return
    try:
        prob.HTML=zipf.read("prob.html")
    except KeyError:
        pass
    try:
        prob.Solve=zipf.read("solve.html")
    except KeyError:
        pass
    prob.save()

def MediaFilePage(request,pk):
    f=get_object_or_404(MadiaFile,pk=int(pk))
    if not f.InitPerm(request.user,"canViewProb"):
        return HttpResponseForbidden()
    return HttpResponseFileDownland(f.File,f.FileName)

@user_passes_test(isAdmin)
def AddProbPage(request):
    if request.method=="POST":
        form=AddProbForm(request.POST,request.FILES)
    else:
        form=AddProbForm()
    if form.is_valid():
        p=Problem.objects.create(Name=form.cleaned_data["name"],Title=form.cleaned_data["name"])
        if form.cleaned_data["file"]:
            p.Data.save(form.cleaned_data["name"]+".zip",form.cleaned_data["file"])
            if form.cleaned_data["loadForZip"]:
                LoadHTML(p)
        return HttpResponseRedirect(reverse("EditProb",kwargs={"name":form.cleaned_data["name"]}))
    return render(request,"addprob.html",locals())

@user_passes_test(isAdmin)
def EditProbPage(request,name,action=None):
    """
    编辑试题
    """
    data,file=None,None
    prob=get_object_or_404(Problem,Name=name)
    if action=="del":
        if request.GET.get("confirm","NO")=="YES":
            prob.delete()
            messages.success(request,u"成功删除")
            return HttpResponseRedirect(reverse("ProbList"))
        else:
            return HttpResponseConfirm(request,[prob],"确认删除题目")
    if request.method=="POST":
        data=request.POST
        file=request.FILES
    form=ProblemForm(data,file,instance=prob)
    if request.method=="POST" and form.is_valid():
        prob=form.save(commit=False)
        if form.cleaned_data["loadForZip"]:
            LoadHTML(prob)
        prob.save()
        messages.success(request,u"成功保存")
        return HttpResponseRedirect(request.path)
    return render(request,"editProb.html",locals())


@login_required
def RegisterContestPage(request,name):
    """
    注册参加比赛
    """
    cont=get_object_or_404(Contest,Name=name)
    if not cont.InitPerm(request.user,"canReg"):
        messages.error(request,u"注册失败，您已经注册，或者比赛不提供注册")
        return HttpResponseGo(request)
    ResultData.objects.create(Contest=cont,User=request.user)
    messages.success(request,u"成功注册比赛")
    return HttpResponseRedirect(reverse("ContList"))

@user_passes_test(isAdmin)
def EditContPage(request,name=None,action=None):
    """
    编辑/添加比赛
    """
    cont,data=None,None
    if name:
        cont=get_object_or_404(Contest,Name=name)
        if action=="del":
            if request.GET.get("confirm","NO")=="YES":
                cont.delete()
                messages.success(request,u"成功删除")
                return HttpResponseRedirect(reverse("ContList"))
            else:
                return HttpResponseConfirm(request,[cont],"确认删除比赛")
    if request.method=="POST":
        data=request.POST
    form = ContestForm(data,instance=cont)
    if request.method=="POST" and form.is_valid():
        cont = form.save(commit=False)
        cont.save()
        messages.success(request,u"成功保存")
    return render(request,"editCont.html",locals())


def ResultPage(request,name):
    cont=get_object_or_404(Contest,Name=name)
    if not cont.InitPerm(request.user,"canViewRes"):
        messages.error(request,u"您无权查看成绩，请等待比赛结束")
        return HttpResponseRedirect(reverse("ContShow",kwargs={"name":name}))
    Set=ResultData.objects.filter(Contest=cont).order_by("-Src").all()
    ProbList=[]
    for p in cont.Prob.all():
        ProbList.append(p.Name)
    for r in Set:
        r.GetResultList(ProbList)
    return render(request,"resList.html",locals())

def UserListPage(request,name):
    cont=get_object_or_404(Contest,Name=name)
    return ShowList(request,"userList.html",ResultData.objects.filter(Contest=cont),cont=cont)

def RankPage(request):
    """
    按通过数显示所有用户，用户列表
    """
    return ShowList(request,"rank.html",UserProfile.objects.order_by("-ACTot"))

def UserRegisterPage(request):
    """
    用户注册
    """
    nex=request.GET.get("next","")
    if nex==request.path:
        return HttpResponseRedirect(request.path)
    if request.method == 'POST':
        form = UserCreationFormWithEmail(request.POST)
        if form.is_valid():
            form.save()
            auth.login(request,auth.authenticate(username=form.cleaned_data["username"],password=form.cleaned_data["password1"]))
            messages.success(request,u"注册成功")
            return HttpResponseRedirect(nex)
    else:
        form = UserCreationFormWithEmail()
    return render(request,"registration/register.html",locals())

def UserProfilePage(request,name=None):
    """
    用户详情
    """

    if name is None:
        user_=request.user
        if user_.is_anonymous():
            return redirect_to_login(request.path)
    else:
        user_=get_object_or_404(User,username=name)

    prob=Problem.objects.all()
    profile=user_.get_profile()
    profile.InitPerm(request.user)
    if request.method == "POST":
        form=DefaultLangForm(request.POST)
        if form.is_valid():
            profile.DefaultLang=form.cleaned_data["Lang"]
            profile.save()
    else:
        form=DefaultLangForm(initial={"Lang":profile.DefaultLang})
    ProbSet=[]
    for p in prob:
        tmp=None
        if p.Name in profile.isAC:
            if profile.isAC[p.Name]:
                tmp="isAC"
            else:
                tmp="hasTry"
        else:
            tmp="notTry"
        ProbSet.append({"Name":p.Name,"Class":tmp})
    return render(request,"profile.html",locals())

@user_passes_test(isAdmin)
def UserPasswordPage(request,name):
    """
    修改/设置密码
    """
    user_=get_object_or_404(User,username=name)
    profile=user_.get_profile()
    profile.InitPerm(request.user)
    data=request.POST
    if not data:
        data=None
    if profile.Perm["canSetPswd"] and user_.pk!=request.user.pk:
        title=u"设置密码"
        form=SetPasswordForm(user_,data=data)
    else:
        title=u"修改密码"
        form=PasswordChangeForm(user_,data=data)
    if request.method=="POST" and form.is_valid():
        form.save()
        messages.success(request,u"操作完成")
        return HttpResponseRedirect(reverse("Profile",kwargs={"name":name}))
    return render(request,"password.html",locals())

@csrf_exempt
def XMLRPCPage(request):
    if request.method == 'POST':
        return HttpResponse(XmlRPC._marshaled_dispatch(request.body),mimetype="application/xml")
    else:
        raise Http404
