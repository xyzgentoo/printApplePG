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

    # print '----------'
    # print html.text
    # print '=========='

    # replace ../../../../../Resources/1163/CSS/screen.css with local modified print.css
        # https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print.css
    # replace ../../../../../Resources/1163/CSS/feedback.css with local feedback.css
        # https://cdn.rawgit.com/xyzgentoo/printApplePG/master/feedback.css

    # <link rel="stylesheet" type="text/css" href="../../../../../Resources/1163/CSS/screen.css">
    updatedHtml = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+screen.css)(\">)', r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print.css\3', html.text)

    updatedHtml = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+feedback.css)(\">)', r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/feedback1.css\3', updatedHtml)

    ## replace img src=".. with img src="https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d
    # items = targetURL.split('/')
    # output = StringIO.StringIO()
    #
    # # 对应一个.. 然后最后一个不是path的一部分 于是-2
    # for i in range(0, len(items) - 2):
    #     output.write(items[i] + "/")
    #
    # imagePrefixURL = output.getvalue()
    imagePrefixURL = getPrefixURL(targetURL)

    updatedHtml = re.sub(r'(<img src=\"../)(\w+)', r'<img src="' + imagePrefixURL + r'\2', updatedHtml)

    items = targetURL.split('/')
    outputPDFName = fileNamePrefix + '_' + items[len(items) - 1] + '.pdf'

    # use pdfkit to generate the pdf - 这里修改encoding是为了避免显示奇怪的字符
    # TODO python encoding这块还不是特别懂...
    updatedHtml = updatedHtml.encode('latin-1')

    # 这样用html文件中转一下,可以正确处理encoding的问题,如果使用pdfkit.from_string()也不能输出updatedHtml,估计是pdfkit内部错误
    tempHtmlName = "./temp.html"
    with codecs.open(tempHtmlName, "w") as f:
        f.write(updatedHtml)

    pdfkit.from_file(tempHtmlName, outputPDFName)

    # clean up temp file
    os.remove(tempHtmlName)

# get prefix URL to replace ../ and get absolute URL
def getPrefixURL(targetURL):
    items = targetURL.split('/')
    output = StringIO.StringIO()

    for i in range(0, len(items) - 2):
        output.write(items[i] + "/")

    ret = output.getvalue()
    return ret

# strip the # part in URL
def getTargetURL(sourceURL):
    return sourceURL.split('#')[0]

# Starting of this program

# REQUIRED
pagePrefix = 'PG_AudioSession_'

# REQUIRED
origURL = 'https://developer.apple.com/library/ios/documentation/Audio/Conceptual/AudioSessionProgrammingGuide/Introduction/Introduction.html'

i = 0

# output introduction page as PDF first
outputPDF(pagePrefix + str(i), origURL)
i += 1

# output other pages as PDFs
prefixURL = getPrefixURL(getTargetURL(origURL))

# TODO 这里看来比较好的做法,也是用splash先将页面渲染一次,然后再parse,能拿到比较准确的数据和结构
htmlObj = requests.get(origURL)

soup = BeautifulSoup(htmlObj.text, 'html.parser')

# 记录已经处理过的URLs
handled = []

links = soup.find_all('span', {'class': 'content_text'})
for link in links:
    dataRenderVersion = link.a["data-renderer-version"]
    print dataRenderVersion
    if dataRenderVersion == '1':
        linkText = link.a["href"]

        if linkText not in handled:
            handled.append(linkText)

            relativePath = '../'
            if linkText.startswith(relativePath):
                # 直接替换最开头的../ 如果有多个 则忽略后面的 这样路径才是正确的
                otherItemURL = prefixURL + linkText[len(relativePath):]
                print otherItemURL
                outputPDF(pagePrefix + str(i), otherItemURL)
                i += 1

print "COOOOOL..."
