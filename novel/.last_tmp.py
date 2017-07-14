# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import os
import time
import urllib2
import urllib
import re
# Create your views here.

def index(request):
    if request.method=='POST':
        title=request.POST['title']
        email=request.POST['email']
        body='''
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        后台下载中，下载完成后邮件发下载地址给你，wait～
        '''
        body=check(title)
        return HttpResponse(body)
    else:
        body='''
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <form method='POST' action='/'>
        小说名称:<br /><input type='text' name='title' /><br />
        邮箱地址:<br /><input type='text' name='email' /><br /><br />
        <input type='submit' value='下载' />
        </form>
        '''
        return HttpResponse(body)

#下载线程
def download(title):
    if os.path.exists('download/%s/0'%title):
        #下载开始
        os.rename('0','1')
        #下载结束
        os.rename('1','0')
            
    elif os.path.exists('download/%s/1'%title):
        while True:
            time.sleep(1)
            if os.path.exists('download/%s/0'%title):
                #下载结束
                pass


#小说查询
def check(title):
    try:url='http://zhannei.baidu.com/cse/search?s=5199337987683747968&q=%s'%title
    except:url='http://zhannei.baidu.com/cse/search?s=5199337987683747968&q=%s'%urllib.quote(title)
    h=urllib2.urlopen(url)
    r=h.read()
    h.close()
    return 'ok'
    a=re.findall('<a cpos="title" href="(.*?)" title="(.*?)" class="result-game-item-title-link" target="_blank">',r)[0]
    titleurl=a[0]
    titlename=a[1]
    description=re.findall('<p class="result-game-item-desc">(.*?)</p>',r,re.S)[0].replace('<em>','').replace('</em>','')
    author=re.findall('作者：</span>.*?<span>(.*?)</span>',r,re.S)[0].strip()
    updatetime=re.findall('更新时间：.*?<span class="result-game-item-info-tag-title">(.*?)</span>',r,re.S)[0].strip()
    lastchapter=re.findall('最新章节：.*?class="result-game-item-info-tag-item" target="_blank">(.*?)</a>',r,re.S)[0].strip()
    body='书名: %s<br />作者: %s<br />更新时间: %s<br />最新章节: %s<br />简介:<br />%s<br />'%(titlename,author,updatetime,lastchapter,description)
    return body.encode('utf-8')