#!/usr/bin/python
# -*- coding: UTF-8 -*-

#import django.forms
from django.forms import *
from models import *
from django.utils.translation import  ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from settings import LangSet

class SubmitForm(Form):
    ProbSet = Problem.objects
    User = None
    Prob = CharField(label=u"题目编号",max_length=50)
    Lang = ChoiceField(LangSet,label=u"编译器")
    File = CharField(label=u"源代码",widget=forms.Textarea(attrs={"rows":"20","cols":"70"}))
    def clean_Prob(self):
        try:
            ProbName=self.cleaned_data["Prob"]
            Prob=self.ProbSet.get(Name=ProbName)
        except Problem.DoesNotExist:
            raise ValidationError(u"题目不存在")
        if not Prob.InitPerm(self.User,"canSubmit"):
            raise ValidationError(u"您没有权限提交该题")
        return Prob

class UserCreationFormWithEmail(UserCreationForm):
    """
    A form that creates a user, with Email
    """
    email = RegexField(label=_("Email"),
        regex=r"\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*",
        error_messages = {
            'invalid': u"Email地址不合法"})

class ContestForm(ModelForm):
    class Meta:
        model = Contest
        exclude = ("RegUser",)

class AddProbForm(Form):
    name = CharField(label=u"编号",max_length=50)
    file = FileField(label=u"数据包",required=False)
    loadForZip = BooleanField(required=False,label=u"从压缩包中读取")
    def clean_name(self):
        if not Problem.objects.filter(Name=self.cleaned_data["name"]).exists():
            return self.cleaned_data["name"]
        else:
            raise ValidationError(u"相同编号的项目已经存在")

class ProblemForm(ModelForm):
    class Media:
        js = (
            "/static/tiny_mce/tiny_mce.js",
            "/static/textareas.js",
        )
    class Meta:
        model = Problem
    isRejudge = BooleanField(required=False,label=u"重新评测")
    loadForZip = BooleanField(required=False,label=u"从压缩包中读取")

class DefaultLangForm(Form):
    Lang = ChoiceField(LangSet,label=u"默认编译器")