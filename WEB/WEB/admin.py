#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.contrib import admin
from WEB.models import *

admin.site.register(Problem)
admin.site.register(Submit)
admin.site.register(UserProfile)
admin.site.register(Contest)
admin.site.register(ResultData)