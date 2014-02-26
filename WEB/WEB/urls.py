#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, include, url
import  settings
from django.contrib.auth.views import login, logout
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from WEB.views import *
from WEB.models import *
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'views.home', name='home'),
    url(r'^$',IndexPage,name="Index"),

    url(r'^problem/$',ProbListPage,name="ProbList"),
    url(r'^problem/(?P<name>[^/]+)/$',ProbShowPage,name="ProbShow"),
    url(r'^problem/(?P<name>[^/]+)/solve$',ProbSolvePage,name="SolveShow"),
    url(r'^problem/(?P<name>[^/]+)/data$',DataDownlandPage,name="DataDownland"),
    url(r'^problem/(?P<name>[^/]+)/edit$',EditProbPage,name="EditProb"),
    url(r'^problem_add$',AddProbPage,name="AddProb"),
    url(r'^problem/(?P<name>[^/]+)/upland/$',AddFilePage,name="Upland"),
    url(r'^problem/(?P<name>[^/]+)/filemanager/$',FileManagerPage,name="FileManager"),
    url(r'^problem/(?P<name>[^/]+)/del$',EditProbPage,kwargs={"action":"del"},name="DelProb"),

    url(r'^login/$',login,name="Login"),
    url(r'^logout/$',logout,name="Logout"),
    url(r'^register/$',UserRegisterPage,name="Register"),

    url(r'^profile/$',UserProfilePage,name="MyProfile"),

    url(r'^user/(?P<name>[^/]+)/$',UserProfilePage,name="Profile"),
    url(r'^user/(?P<name>[^/]+)/password$',UserPasswordPage,name="Password"),

    url(r'^rank$',RankPage,name="Rank"),

    url(r'^submit/$',SubmitPage,name="Submit"),
    url(r'^submit/(?P<cont>[^/]+)/$',SubmitPage,name="SubmitX"),
    url(r'^state/$',StatePage,name="State"),
    url(r'^detail/(?P<pk>\d*)/$',DetailPage,name="Detail"),
    url(r'^rejudge/$',StatePage,name="Rejudge",kwargs={"action":"rejudge"}),

    url(r'^contest/$',ContListPage,name="ContList"),
    url(r'^contest/(?P<name>[^/]+)/$',ContShowPage,name="ContShow"),
    url(r'^contest/(?P<name>[^/]+)/register/$',RegisterContestPage,name="RegCont"),
    url(r'^contest/(?P<name>[^/]+)/rank',ResultPage,name="Result"),
    url(r'^contest/(?P<name>[^/]+)/list',UserListPage,name="UserList"),
    url(r'^contest/(?P<name>[^/]+)/edit',EditContPage,name="EditCont"),
    url(r'^contest/(?P<name>[^/]+)/del',EditContPage,name="DelCont",kwargs={"action":"del"}),
    url(r'^contest_add',EditContPage,name="AddCont"),
    # url(r'^PySQOJ/', include('foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^xmlrpc$',XMLRPCPage,name="XMLPRC"),
    url(r'^media/(?P<pk>\d*)$', MediaFilePage),
)
