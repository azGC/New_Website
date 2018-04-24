# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from templates.dashboard.Connect_DB \
    import getLevel1Attributes, getLevel2Attributes
import json
from django import forms
from django.shortcuts import render,render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login


class UserForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', widget=forms.PasswordInput())


def my_login(request):
    # next__ = request.get[next]
    if request.method == 'POST':
        userform = UserForm(request.POST)
        if userform.is_valid():
            username = userform.cleaned_data['username']
            password = userform.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render_to_response('dashboard/index.html', {'userform': userform})
                    # return render_to_response(next__, {'userform': userform})
                else:
                    return HttpResponse('wrong username or password, please re-input')
            else:
                return HttpResponse('wrong username or password, please re-input')
        else:
            return HttpResponse('wrong username or password, please re-input')
    else:
        userform = UserForm()
        return render_to_response('dashboard/login.html',{'userform':userform})

# @login_required
# def my_logout(request):
#     request = render_to_response('dashboard/login.html')
#     #清除cookie里保存的username
#     logout(request)
#     return request


# index page
def index(request):
    return render(request, 'dashboard/index.html')
# car dashboard page
@login_required
def carOwnerChartPage(request):
    return render(request, 'dashboard/carEchartPage.html')

# get car page data
# @login_required
def carOwnerChart(request):
    # page 对应原页面 page 1-4
    target = request.GET.get('a', '')
    page_1_brand = getLevel1Attributes(target)
    page_1_model = getLevel1Attributes(target)
    dict = {'page_1_brand': page_1_brand,
                'page_1_model': page_1_model,}
    return HttpResponse(json.dumps(dict), content_type='application/json')

