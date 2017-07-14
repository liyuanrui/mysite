# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
import os
import time

import urllib
import re
import _thread
import zipfile

#from androidhelper import Android
#d=Android()
#~
# Create your views here.
os.chdir('/sdcard/qpython/projects3/mysite')

viewport='<meta name="viewport" content="width=device-width, initial-scale=1" />'
hurl='http://wap.xxbiquge.com'


def index(request):
    if request.method=='POST':
        title=request.POST['title']
        
        body='''
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        '''
        body=body+check(title)
        return HttpResponse(body)
    else:
        body='''
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <small>Welcome! 下载和在线等都要先查询，下载要解压</small><br /><hr />
        小说名称:<br />
        <textarea id='title' rows='1' cols='21'></textarea><br /><br />
        
        <button id='check'>查询</button>&nbsp;&nbsp;&nbsp;&nbsp;<button id='start'>下载</button>&nbsp;&nbsp;&nbsp;&nbsp;<button id='wait'>在线等</button><br /><br />
        <small id='show'></small>
        <script src="http://libs.baidu.com/jquery/1.10.2/jquery.min.js"></script>
        <script>
        $(document).ready(function(){
            $("#check").click(function(){
                var title=$("#title").val();
                $.post('/',{
                        title:title
                },
                function(data,status){
                        $('#show').html(data);
                }) })
            $("#start").click(function(){
                var title=$("#title").val();
                var show =$("#show").html();
                $.post('down',{
                        title:title,
                        show:show
                        
                },
                function(data,status){
                        $('#show').html(data);
                }) })
            $("#wait").click(function(){
                var title=$("#title").val();
                var show =$("#show").html();
                $.post('wait',{
                        title:title,
                        show:show
                        
                },
                function(data,status){
                        $('#show').html(data);
                }) })
                })
        </script>
        '''
        return HttpResponse(body)

def down(request):
    if request.method=='POST':
        show=request.POST['show']
        try:
            title=re.findall('书名: (.*?)<br>作者',show)[0]
            author=re.findall('作者: (.*?)<br>更新',show)[0]
            chapterurl=re.findall('章节列表: (.*?)<br>',show)[0]
            
            if not os.path.exists('novel/download/%s.%s'%(title,author)):
                os.mkdir('novel/download/%s.%s'%(title,author))
                with open('novel/download/%s.%s/0'%(title,author),'w') as f:
                    pass
            if not os.path.exists('novel/download/%s.%s/%s.txt'%(title,author,title)):
                with open('novel/download/%s.%s/%s.txt'%(title,author,title),'w') as f:
                    pass
            if not os.path.exists('novel/download/%s.%s/%s.log'%(title,author,title)):
                with open('novel/download/%s.%s/%s.log'%(title,author,title),'w') as f:
                    pass
            if os.path.exists('novel/download/%s.%s/1'%(title,author)):
                return HttpResponse(viewport+'正在下载，请留意邮件提醒或在线等')
            _thread.start_new_thread(download,(title,author,chapterurl))
            return HttpResponse(viewport+'正在下载，请留意邮件提醒或在线等～')
        except Exception as e:
            return HttpResponse(viewport+'先点查询再下载')


#下载线程
def download(title,author,chapterurl):
    cc=chapterurl.split('/')[-2]
    if os.path.exists('novel/download/%s.%s/0'%(title,author)):
        #下载开始
        os.rename('novel/download/%s.%s/0'%(title,author),'novel/download/%s.%s/1'%(title,author))
        try:
            h=urllib.request.urlopen(chapterurl)
            r=h.read().decode()
            h.close()
            with open('novel/download/%s.%s/%s.log'%(title,author,title),'r') as fr:
                rf=fr.read()
            #exit()
            chapterlist=[]
            bo=re.findall('<p><a href="(.*?).html">(.*?)</a></p>',r)
            for i in bo:
                if i[1] not in rf:chapterlist.append(i)
            fw=open('novel/download/%s.%s/%s.txt'%(title,author,title),'a+')
            fl=open('novel/download/%s.%s/%s.log'%(title,author,title),'a+')
            #fd=open('novel/download/%s.%s/1'%(title,author),'w')
            for i in range(len(chapterlist)):
             
                uurl=hurl+'/'+cc+'/'+chapterlist[i][0]+'.html'
                body=urllib.request.urlopen(uurl)
                read=body.read().decode()
                article=re.findall('style="text-align:center;color:red;">『章节错误,点此举报』</a></p>(.*?)<p style="width:100%;text-align:center;">',read,re.S)[0]
                article=article.replace("<br />","\n").replace("&nbsp;"," ").replace("<br>","\n").replace("<br/>","\n")
                article=chapterlist[i][1]+'\n\n'+article+'\n\n\n\n\n'
                fw.write(article)
                percent=i/len(chapterlist)
                ss='%.2f'%percent
                fw.write(article)
                fl.write(chapterlist[i][1]+'\n')
                fw.flush()
                fl.flush()
                with open('novel/download/%s.%s/1'%(title,author),'w') as fd:
                    fd.write(ss)
                    fd.flush()
        except Exception as e:
            with open('novel/download/%s.%s/error'%(title,author),'a+') as fd:
                fd.write('\n'+str(e))
        finally:
            #下载结束
            with open('novel/download/%s.%s/1'%(title,author),'w') as fd:
                fd.write(time.strftime('%Y-%m-%d %H:%M:%S'))
            os.rename('novel/download/%s.%s/1'%(title,author),'novel/download/%s.%s/0'%(title,author))
            fw.close()
            fl.close()
            
            
            
def wait(request):
    if request.method=='POST':
        show=request.POST['show']
        try:
            title=re.findall('书名: (.*?)<br>作者',show)[0]
            author=re.findall('作者: (.*?)<br>更新',show)[0]
            if os.path.exists('novel/download/%s.%s/0'%(title,author)):
                with open('novel/download/%s.%s/0'%(title,author)) as fg:
                    ctime=fg.read()
                z=zipfile.ZipFile('novel/download/%s.%s/%s.zip'%(title,author,title),'w',compression=zipfile.ZIP_DEFLATED)
                z.write('novel/download/%s.%s/%s.txt'%(title,author,title))
                z.close()
                ok='http://127.0.0.1:8001/%s.%s/%s.zip'%(urllib.parse.quote(title),urllib.parse.quote(author),urllib.parse.quote(title))
                ok=viewport+'<a href="%s">%s.zip(下载时间:%s)</a>'%(ok,title,ctime)
            elif os.path.exists('novel/download/%s.%s/1'%(title,author)):
                with open('novel/download/%s.%s/1'%(title,author)) as fq:
                    percent=fq.read()
                ok=viewport+'下载进度: %s'%percent+'%'
            return HttpResponse(ok)
        except Exception as e:
            return HttpResponse(viewport+str(e))

#小说查询
def check(title):
    try:
        url='http://zhannei.baidu.com/cse/search?s=5199337987683747968&q=%s'%urllib.parse.quote(title)
        h=urllib.request.urlopen(url)
        r=h.read().decode()
        h.close()
        #return 'ok'
        a=re.findall('<a cpos="title" href="(.*?)" title="(.*?)" class="result-game-item-title-link" target="_blank">',r)[0]
        titleurl=a[0]
        titlename=a[1]
        chapterurl=titleurl.replace('www','wap')+'all.html'
        description=re.findall('<p class="result-game-item-desc">(.*?)</p>',r,re.S)[0].replace('<em>','').replace('</em>','')
        author=re.findall('作者：</span>.*?<span>(.*?)</span>',r,re.S)[0].strip()
        updatetime=re.findall('更新时间：.*?<span class="result-game-item-info-tag-title">(.*?)</span>',r,re.S)[0].strip()
        lastchapter=re.findall('最新章节：.*?class="result-game-item-info-tag-item" target="_blank">(.*?)</a>',r,re.S)[0].strip()
        body='书名: %s<br />作者: %s<br />更新时间: %s<br />最新章节: %s<br />简介:<br />%s<br />章节列表: %s<br />'%(titlename,author,updatetime,lastchapter,description,chapterurl)
        return body
    except Exception as e:
        return '查询失败，试多几次一定行'


