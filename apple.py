# -*- coding: utf-8 -*-

__author__ = 'lihong'

import requests
import re
import pdfkit
import StringIO
from bs4 import BeautifulSoup
import codecs
import os

# Quartz 2D Programming Guide
# targetURL = 'https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/Introduction/Introduction.html#//apple_ref/doc/uid/TP40007533-SW1'
# targetURL = 'https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/dq_overview/dq_overview.html#//apple_ref/doc/uid/TP30001066-CH202-TPXREF101'
# targetURL = 'https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/dq_context/dq_context.html#//apple_ref/doc/uid/TP30001066-CH203-TPXREF101'
# targetURL = 'https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/dq_paths/dq_paths.html#//apple_ref/doc/uid/TP30001066-CH211-TPXREF101'

def outputPDF(fileNamePrefix, sourceURL):
    # for Apple doc url, remove the part after #
    targetURL = getTargetURL(sourceURL)
    print targetURL

    # load url into html text strings
    html = requests.get(targetURL)

    # 替换apple css为我自己修改后的css,为了输出print friendly样式的页面
    # <link rel="stylesheet" type="text/css" href="../../../../../Resources/1163/CSS/screen.css">
    updatedHtml = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+screen.css)(\">)', r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print.css\3', html.text)

    updatedHtml = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+feedback.css)(\">)', r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/feedback1.css\3', updatedHtml)

    ## replace img src=".. with img src="https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d
    resPrefixURL = getPrefixURL(targetURL)

    # 替换img的相对路径
    updatedHtml = re.sub(r'(<img src=\"../)(\w+)', r'<img src="' + resPrefixURL + r'\2', updatedHtml)

    # 注意 那几个js最好不要替换,要不里面也会报出找不到content的问题,pdfkit执行的时候就会报错了

    items = targetURL.split('/')
    outputPDFName = fileNamePrefix + '_' + items[len(items) - 1] + '.pdf'

    # use pdfkit to generate the pdf - 这里修改encoding是为了避免显示奇怪的字符
    # TODO python encoding这块还不是特别懂...
    updatedHtml = updatedHtml.encode('latin-1')
    # print updatedHtml

    # 这样用html文件中转一下,可以正确处理encoding的问题,如果使用pdfkit.from_string()也不能输出updatedHtml,估计是pdfkit内部错误
    tempHtmlName = "./temp.html"
    with codecs.open(tempHtmlName, "w") as f:
        f.write(updatedHtml)

    # 从html文件生成pdf
    pdfkit.from_file(tempHtmlName, outputPDFName)

    # clean up temp file
    os.remove(tempHtmlName)
    pass

# get prefix URL to replace ../ and get absolute URL
def getPrefixURL(targetURL):
    items = targetURL.split('/')
    output = StringIO.StringIO()

    # 对应一个.. 然后最后一个不是path的一部分 于是-2 - 只把第一个../替换成URL中的部分,其他的相对路径在这个基础上就找到了
    for i in range(0, len(items) - 2):
        output.write(items[i] + "/")

    ret = output.getvalue()
    return ret

# strip the # part in URL
def getTargetURL(sourceURL):
    return sourceURL.split('#')[0]

# Starting of this program

# REQUIRED
filenamePrefix = 'PG_Quartz2D_'

# REQUIRED - 这里记录去掉域名的部分,方便和后面的统一
origURL = '/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/Introduction/Introduction.html'

# REQUIRED - DO NOT CHANGE FOR APPLE Programming Guides
urlPrefix = 'https://developer.apple.com'

i = 0

# 记录已经处理过的URLs
handled = [origURL]

# output introduction page as PDF first
finalOrigURL = urlPrefix + origURL
print 'orig: ' + finalOrigURL
outputPDF(filenamePrefix + str(i), finalOrigURL)
i += 1

# output other pages as PDFs

print 'start splashing...'

# 这里看来比较好的做法,也是用splash先将页面渲染一次,然后再parse,能拿到比较准确的数据和结构

# Start splash in terminal first, or it won't work
# Steps
# * Run = VBoxManage startvm default = in terminal to start Virtualbox machine named 'default'
# * Run = eval "$(docker-machine env default)" = in terminal to init docker environment
# * Run = docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash & = in terminal to start splash
# * Run = docker-machine ip default = in terminal to get the IP of docker machine
splashURL = 'http://192.168.99.100:8050/render.html?timeout=60&url=' + finalOrigURL
htmlObj = requests.get(splashURL)

soup = BeautifulSoup(htmlObj.text, 'html.parser')

sections = soup.find_all('span', {'class': 'sectionName'})
# 直接忽略
for section in sections:
    link = getTargetURL(section.a['href'])

    # 这里得到的link都是不包含域名的版本
    if link not in handled:
        finalURL = urlPrefix + link
        print 'new: ' + finalURL
        outputPDF(filenamePrefix + str(i), finalURL)
        i += 1
        handled.append(link)

print "COOOOOL..."
