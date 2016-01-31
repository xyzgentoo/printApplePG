# -*- coding: utf-8 -*-

__author__ = 'lihong'

import requests
import re
import pdfkit
import StringIO
from bs4 import BeautifulSoup
import codecs
import os


# 将Apple Programming Guide中的内容,生成print friendly pdfs
def output_pdf(file_name_prefix, source_url):
    # for Apple doc url, remove the part after #
    target_url = get_target_url(source_url)
    print target_url

    # load url into html text strings
    html = requests.get(target_url)

    # PG 样式2 -
    # 另一个系列的Programming guides
    # 例如: https://developer.apple.com/library/ios/documentation/UserExperience/Conceptual/AutolayoutPG/index.html
    # https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print-style-1.5.1.css
    # https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print-feedback-1.5.1.css
    updated_html_text = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+style-1.5.1.css)(\">)',
                               r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print-style-1.5.1.css\3',
                               html.text)
    updated_html_text = re.sub(r'(<link rel=\"stylesheet\" type=\"text/css\" href=\")(.+feedback-1.5.1.css)(\">)',
                               r'\1https://cdn.rawgit.com/xyzgentoo/printApplePG/master/print-feedback-1.5.1.css\3',
                               updated_html_text)

    ## replace img src=".. with
    # img src="https://developer.apple.com/library/ios/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d
    res_prefix_url = get_prefix_url(target_url)

    # 替换img的相对路径
    updated_html_text = re.sub(r'(<img src=\"../)(\w+)', r'<img src="' + res_prefix_url + r'\2', updated_html_text)

    # 注意 那几个js最好不要替换,要不里面也会报出找不到content的问题,pdfkit执行的时候就会报错了

    items = target_url.split('/')
    output_pdf_name = file_name_prefix + '_' + items[len(items) - 1] + '.pdf'

    # use pdfkit to generate the pdf - 这里修改encoding是为了避免显示奇怪的字符
    # TODO python encoding这块还不是特别懂...
    updated_html_text = updated_html_text.encode('latin-1')
    # print updated_html_text

    # 这样用html文件中转一下,可以正确处理encoding的问题,如果使用pdfkit.from_string()也不能输出updatedHtml,估计是pdfkit内部错误
    temp_html_file_name = "temp.html"
    with codecs.open(temp_html_file_name, "w") as f:
        f.write(updated_html_text)

    # 从html文件生成pdf
    pdfkit.from_file(temp_html_file_name, output_pdf_name)

    # clean up temp file
    os.remove(temp_html_file_name)
    pass


# get prefix URL to replace ../ and get absolute URL
def get_prefix_url(target_url):
    items = target_url.split('/')
    output = StringIO.StringIO()

    # 对应一个.. 然后最后一个不是path的一部分 于是-2 - 只把第一个../替换成URL中的部分,其他的相对路径在这个基础上就找到了
    for i in range(0, len(items) - 2):
        output.write(items[i] + "/")

    ret = output.getvalue()
    return ret


# strip the # part in URL
def get_target_url(source_url):
    return source_url.split('#')[0]


# Starting of this program

# REQUIRED
filename_prefix = 'PG_AutoLayout_'

# REQUIRED - 这里记录去掉域名的部分,方便和后面的统一
orig_url = '/library/ios/documentation/UserExperience/Conceptual/AutolayoutPG/index.html'

# REQUIRED - DO NOT CHANGE FOR APPLE Programming Guides
domain_prefix = 'https://developer.apple.com'

i = 0

# 记录已经处理过的URLs
handled = [orig_url]

# output introduction page as PDF first
final_orig_url = domain_prefix + orig_url
print 'orig: ' + final_orig_url
output_pdf(filename_prefix + str(i), final_orig_url)
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
splashURL = 'http://192.168.99.100:8050/render.html?timeout=60&url=' + final_orig_url
html_obj = requests.get(splashURL)

soup = BeautifulSoup(html_obj.text, 'html.parser')

sections = soup.find_all('li', {'class': 'nav-chapter'})
print "len(sections): " + str(len(sections))

# 直接忽略
for section in sections:
    link = get_target_url(section.a['href'])
    print link

    # # 这里要过滤一下API Reference的链接
    # if None == re.match(r'(\/.+Reference\/.*\/index.html)', link):
    #     # 这里得到的link都是不包含域名的版本
    #     if link not in handled:
    #         final_url = domain_prefix + link
    #         print 'new: ' + final_url
    #         output_pdf(filename_prefix + str(i), final_url)
    #         i += 1
    #         handled.append(link)
    #
    #         # 如果处理完版本更新的历史,就停止了,因为有些guides后面会跟着其他的链接,不支持的格式
    #         if link.endswith('RevisionHistory.html'):
    #             print '--- TO END ---'
    #             break

print '*' * 50
