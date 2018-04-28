# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from templates.dashboard.Connect_DB \
    import getBrandShare, getModelShare, getModelList, getNational, getTop
import json
from django import forms
from django.shortcuts import render, render_to_response
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
    # Model_List
    target = request.GET.get('a', '')
    if target == 'model_list':
        model_list = getModelList(target)
        return HttpResponse(json.dumps(model_list), content_type='application/json')
    # 进入model查找
    if target != '"全国"':
        target_list = eval(target)
        if len(target_list) == 3:
            # model_number = target_list[2].count(',') + 1
            page_1_model = getModelShare(target_list)
            # dict = {
            #     'page_1_model': page_1_model,
            #     'model_number': model_number
            # }
            return HttpResponse(json.dumps(page_1_model), content_type='application/json')

    else:
        page_1_brand = getBrandShare(target)
        page_1_national = getNational(target)
        page_1_top = getTop()

        dict = {'page_1_brand': page_1_brand,
                    'page_1_national': page_1_national,
                    'page_1_top': page_1_top
                }
        return HttpResponse(json.dumps(dict), content_type='application/json')

