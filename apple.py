# -*- coding: utf-8 -*-

__author__ = 'lihong'

import requests
import re
import pdfkit
import StringIO
from bs4 import BeautifulSoup

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

    # use pdfkit to generate the pdf
    pdfkit.from_string(updatedHtml, outputPDFName)

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
pagePrefix = 'PG_Quartz2D_'

# REQUIRED
origURL = 'https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/Introduction/Introduction.html#//apple_ref/doc/uid/TP40007533-SW1'

i = 0

# output introduction page as PDF first
outputPDF(pagePrefix + str(i), origURL)
i += 1

# output other pages as PDFs
prefixURL = getPrefixURL(getTargetURL(origURL))

htmlObj = requests.get(origURL)

soup = BeautifulSoup(htmlObj.text, 'html.parser')

links = soup.find_all('span', {'class': 'content_text'})
for link in links:
    linkText = link.a["href"]
    if linkText.startswith('../'):
        otherItemURL = linkText.replace('../', prefixURL)
        outputPDF(pagePrefix + str(i), otherItemURL)
        i += 1

print "COOOOOL..."
