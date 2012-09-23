#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib
import codecs
from feedparser import _getCharacterEncoding

class MainInfo(object):
    """针对不同的站点，获取标题，内容，下一页链接的方式可能会不同
    针对不同的网站只需要去修改相应方法中的正则表达式即可，或者使用任何你喜欢的方式，但是必须保证这几个方法的名称不改变，另外需要返回值 """
    def __init__(self, url):
        super(MainInfo, self).__init__()
        self.url = url   #网页URL
        self.req = urllib.urlopen(url)
        self.text = self.req.read()
        self.encoding = _getCharacterEncoding(self.req.headers, self.text)[0]
    def get_PG_Num(self):
        pg=re.search(r'([^./]*).html$',self.url).group(1)
        return pg
    def get_main_content(self):
        content=re.search(r'<div class="content-body">[\s\S]*<div style="clear:both">', self.text).group()
        return content
    def get_nextpage_url(self):
        nexturl=None
        try:
            nexturl=re.search(r"<a\s*id=\"xiayipian\"\s*class=\"r\"\s*href=\"([^\"]*)",self.text)
            if nexturl is not None:
                nexturl=nexturl.group(1)
        finally:
            pass
        return nexturl
    def get_title(self):
        title=re.search(r'<H1>([^<]*)</H1>',self.text).group(1)
        return title