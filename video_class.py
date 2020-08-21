#!/usr/bin/env python3
from bs4 import BeautifulSoup
import threading
import os
import requests
import time
import re
import urllib
import sys

def getHTMLText(url):
    headers = {
        'Host': 'http://www.kuyunzy.tv',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40'}
    try:
        r = requests.post(url, headers=headers)  
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"

def search_mov(mov_name):
        url = 'http://www.kuyunzy.tv/index.php?m=vod-search&wd=' + mov_name
        print("查询到的资源信息如下：")
        html = getHTMLText(url)
        # print(html)
        title_number = 1
        soup = BeautifulSoup(html, "html.parser")
        # print(soup)
        gather= []
        for k in soup.find_all(href=re.compile(r'\?m=vod\-detail\-id\-(\d*)\.html')):
            # print(k)
            try:
                link = k['href']  # 查a标签的href值
                # print(link)
                s = k.string
                # print(s)
                title = "".join(s.split())  # 查a标签的string
                # print(title)
                print('%d、%s http://www.kuyunzy.tv/%s' % (title_number, title, link))
                title_number = title_number + 1
                url2 = 'http://www.kuyunzy.tv/' + link
                a = {'title': title,'link': url2}
                gather.append(a)
                # print(gather)
                # print(url2)
                html2 = getHTMLText(url2)
                # print(html2)
            except:
                continue
        if len(gather) > 0:
            pass
        else:
            print('没有搜索到该电影')
        return gather
        # print(gather)

def select_dl(movlink):
    # movlink: 电影链接
    print('The value of v_url is %s' %(movlink))
    html2 = getHTMLText(movlink)
    # print(html2)
    downgather = []
    soup2 = BeautifulSoup(html2, "html.parser")
    # print(soup2)
    for h in soup2.find_all('a' ):
        try:
            downlink = h.string
            # print(downlink)
            if downlink.endswith('.mp4'):
                print(downlink)
                finalink = re.findall(r'http:\/\/.*\.mp4',downlink)
                # print(finalink)
                downgather.append(finalink[0])
            else:
                continue
        except:
            continue
    # print(downgather)
    return downgather


def view_bar(num, total):  #显示进度条
    rate = num/total
    rate_num = int(rate * 100)
    number=int(50*rate)
    r = '\r[%s%s]%d%%' % ("#"*number, " "*(50-number), rate_num, )
    print("\r {}".format(r),end=" ")   #\r回到行的开头

def search(self,text):
    print("Input: " + text)

class Getfile():  #下载文件
    def __init__(self,url):
        self.url=url
        #self.filename=filename
        self.re=requests.head(url,allow_redirects=True)  #运行head方法时重定向

    def getsize(self):
        try:
            self.file_total=int(self.re.headers['Content-Length']) #获取下载文件大小    
            return self.file_total
        except:
            print('无法获取下载文件大小')
            exit()
   
    def downfile(self,file_pname):  #下载文件
        self.r = requests.get(self.url,stream=True)
        with open(file_pname, "wb") as code:
            for chunk in self.r.iter_content(chunk_size=1024): #边下载边存硬盘
                if chunk:
                    code.write(chunk)
        time.sleep(1)
        #print ("\n下载完成")
        
    def downprogress(self,file_pname):
        self.file_pname=file_pname
        self.file_size=0
        self.file_total=self.getsize()
        while self.file_size<self.file_total:  #获取当前下载进度
            time.sleep(1)
            self.down_rate=(os.path.getsize(self.file_pname)-self.file_size)/1024/1024
            self.down_time=(self.file_total-self.file_size)/1024/1024/self.down_rate
            self.file_size=os.path.getsize(self.file_pname)
            # if os.path.exists(self.file_pname):
            #     print (" "+str('%.2f' %self.down_rate+"MB/s"),end="")
            # print (" "+str(int(self.down_time))+"s",end="")
            # print (" "+str('%.2f' %(self.file_size/1024/1024))+"MB",end="")
            # view_bar(self.file_size, self.file_total)
            progress = int((self.file_size/self.file_total) * 100)
            return progress
    
