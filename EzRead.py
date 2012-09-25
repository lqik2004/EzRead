#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
EzRead can fetch WebPage content with awesome layout and send it to your kindle automatically
You can write your own template file and link it to bookinfo.cfg

Author:lqik2004

EzRead contains free software "SENDTOKINDLE" which author is kparal（https://github.com/kparal/sendKindle.git）

'''
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ConfigParser
from optparse import OptionParser
import os
import smtplib
import sys
from StringIO import StringIO
from email import encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.generator import Generator
from email.header import Header
import re
import urllib2
import urllib
import codecs
from feedparser import _getCharacterEncoding
import html2text
import string
import subprocess
import time

_version = '1.3'
realPath=os.path.dirname(os.path.realpath(__file__))
####################SENDTOKINDLE####################
class SendKindle:
    conffile=realPath+'/sendkindle.cfg'
    sample_conf='''  [SENDTOKINDLE]
  smtp_server = smtp.gmail.com
  smtp_port = 465
  smtp_login = username
  user_email = username@gmail.com
  kindle_email = username@free.kindle.com
  smtp_password = password
  convert = False'''
    smtp_password = None

    def __init__(self):
        self.read_config()
    def read_config(self):
        config = ConfigParser.SafeConfigParser()
        try:
            if not config.read([os.path.expanduser(self.conffile)]):
                raise IOError('%s could not be read' % self.conffile)
            self.smtp_server = config.get('SENDTOKINDLE', 'smtp_server')
            self.smtp_port = config.getint('SENDTOKINDLE', 'smtp_port')
            self.smtp_login = config.get('SENDTOKINDLE', 'smtp_login')
            self.user_email = config.get('SENDTOKINDLE', 'user_email')
            self.kindle_email = config.get('SENDTOKINDLE', 'kindle_email')
            self.smtp_password =config.get('SENDTOKINDLE', 'smtp_password')
            self.convert = config.getboolean('SENDTOKINDLE', 'convert')
        except (IOError, ConfigParser.Error, ValueError) as e:
            print e
            message = "You're missing a program configuration file. Please " \
                      "create %s with the following example content:\n" \
                      "%s" % (self.conffile, self.sample_conf)
            print >> sys.stderr, message
            sys.exit(3)

    def send_mail(self,files):
        '''Send email with attachments'''
        print('Waiting for sending file to email...It may takes a few minutes')
        # create MIME message
        msg = MIMEMultipart()
        msg['From'] = self.user_email
        msg['To'] = self.kindle_email
        msg['Subject'] = 'Convert' if self.convert else 'Sent to Kindle'
        text = 'This email has been automatically sent by EzRead tool.'
        msg.attach(MIMEText(text))

        # attach files
        for file_path in files:
            msg.attach(self.get_attachment(file_path))

        # convert MIME message to string
        fp = StringIO()
        gen = Generator(fp, mangle_from_=False)
        gen.flatten(msg)
        msg = fp.getvalue()

        # send email
        mailServer = smtplib.SMTP_SSL(host=self.smtp_server, port=self.smtp_port)
        mailServer.login(self.smtp_login, self.smtp_password)
        mailServer.sendmail(self.user_email, self.kindle_email, msg)
        mailServer.close()

        print('Sent email to %s' % self.kindle_email)

    def get_attachment(self, file_path):
        '''Get file as MIMEBase message'''
        file_ = open(file_path, 'rb')
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file_.read())
        file_.close()
        encoders.encode_base64(attachment)
        name=os.path.basename(file_path).decode("utf-8").encode('utf-8')
        attachment.add_header('Content-Disposition', 'attachment',
                              filename=name)
        
        return attachment


################CORE CLASS##################
class GenTextFiles(object):
    """Generate Text File(s) From Web and Send it/them To Your Kindle"""
    def __init__(self,kindlegenBoolValue,sendBoolValue):
        super(GenTextFiles, self).__init__()
        self.kindlegenBoolValue=kindlegenBoolValue
        self.sendBoolValue=sendBoolValue
        self.filenames=[]
        #Read books config file 
        self.booksConfig=[]
        self.load_config()
        for book in self.booksConfig:
            #clean filenames' cache
            self.filenames=[]
            url=book['url']
            moduleName=book['ExtendFile']
            ExtendFile=__import__(moduleName)
            func=ExtendFile.MainInfo(url)
            text=func.get_main_content()
            pg=func.get_PG_Num()
            perfix=book['filename_perfix']
            texttitle=func.get_title()
            textencoding=func.encoding
            nexturl=func.get_nextpage_url()
            fname=perfix+pg+".txt"

            
            files = os.listdir(realPath)  
            result=fname in files
            if result is False:
                #不存在
                self.genNewFile(perfix,pg,text,texttitle,textencoding)

            while nexturl is not None:
                #write url to configfile as currenturl
                self.set_config(book['section'],'url',nexturl)
                url=nexturl
                moduleName=book['ExtendFile']
                ExtendFile=__import__(moduleName)
                func=ExtendFile.MainInfo(url)
                text=func.get_main_content()
                pg=func.get_PG_Num()
                perfix=book['filename_perfix']
                texttitle=func.get_title()
                textencoding=func.encoding
                nexturl=func.get_nextpage_url()
                fname=perfix+pg+".txt"
                self.genNewFile(perfix,pg,text,texttitle,textencoding)
            if self.filenames:
                sendfilePath=self.filenames
                if self.kindlegenBoolValue:
                    sendfilePath=self.makeMobiVersion(self.filenames,book['author'],book['bookname'],perfix)
                if self.sendBoolValue:
                    #send files to kindle
                    kindle = SendKindle()
                    kindle.send_mail(sendfilePath)
    def load_config(self):
        config_path=realPath+'/bookinfo.cfg'
        config=ConfigParser.RawConfigParser()
        try:
            if not config.read(config_path):
                raise IOError('%s could not be read' % config_path)
            for book in config.sections():
                filename_perfix=config.get(book,'filename_perfix')
                ExtendFile=config.get(book,'ExtendFile')
                author=config.get(book,'author')
                bookname=config.get(book,'bookname')
                url=config.get(book,'url')
                section=book
                dic={'filename_perfix':filename_perfix,'ExtendFile':ExtendFile,'author':author,'bookname':bookname,
                'url':url,'section':section}
                self.booksConfig.append(dic)
                #print filename_perfix,url,ExtendFile,author,bookname

        except (IOError, ConfigParser.Error, ValueError) as e:
            print e
            message = "You're missing a program configuration file. Please " \
                      "create %s with the following example content:\n" \
                      "%s" % (self.conffile, self.sample_conf)
            print >> sys.stderr, message
            sys.exit(3)

    def set_config(self,section,item,content):
        config_path=realPath+'/bookinfo.cfg'
        config=ConfigParser.RawConfigParser()
        try:
            if not config.read(config_path):
                raise IOError('%s could not be read' % config_path)
            config.set(section,item,content)

        except (IOError, ConfigParser.Error, ValueError) as e:
            print e
            message = "You're missing a program configuration file. Please " \
                      "create %s with the following example content:\n" \
                      "%s" % (self.conffile, self.sample_conf)
            print >> sys.stderr, message
            sys.exit(3)
        with open(config_path, 'wb') as configfile:
            config.write(configfile)
        
            
    def searchNextURL(self,nexturl):
        if nexturl is not None:
            wirte_lastURlFile=codecs.open(realPath+"/lasturl.txt","w",'utf-8')
            wirte_lastURlFile.write(nexturl)
            wirte_lastURlFile.close()
            #print nexturl
            return True
         
    def genNewFile(self,perfix,pg,content,texttitle,textencoding): 
        #title
        title=texttitle
        title=title.decode("utf-8")
        #print title
        
        text=content    
        encoding = textencoding
        if encoding == 'us-ascii': encoding = 'utf-8'
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = text.decode(chardet.detect(text)['encoding'])            
        output=html2text.HTML2Text()
        output.ignore_links=True
        ot_string=output.handle(text)
        ot_string=title+u"\n\n"+ot_string+u"\n感谢使用本书的自动生成工具EzRead\n作者：lqik2004#gmail.com\nTwitter:@lqik2004"
        filename=realPath+"/"+perfix+pg+".txt"
        ot_file=codecs.open(filename,'w','utf-8')
        ot_file.write(ot_string)
        ot_file.close()
        print "生成新文件：%s"%(filename)
        self.filenames.append(filename)

    def makeMobiVersion(self,txtfilenames,author,bookname,perfix):
        mobifilePath=MakeMobiFiles(author,bookname,perfix).genMobiFiles(txtfilenames)
        return mobifilePath

#@@@@@@@@@@@@@@@@--MOBI FILES--@@@@@@@@@@@@@@@@@@@#
class MakeMobiFiles(object):
    """docstring for MakeMobiFiles"""
    def __init__(self,author,bookname,filename_perfix):
        super(MakeMobiFiles, self).__init__()
        self.author=author
        self.bookname=bookname
        self.perfix=filename_perfix

    def genMobiFiles(self,txtfilenames):
        mobifilePath=[]
        coverPath=realPath+'/Cover.jpg'
        htmlFilePathAndTitle=self.make_content_html(txtfilenames)
        tocHtmlPath=self.make_TOC_html(htmlFilePathAndTitle)
        tocNcxPath=self.make_TOC_ncx(htmlFilePathAndTitle,tocHtmlPath)
        opfPath=self.make_OPF(coverPath,tocNcxPath,tocHtmlPath,htmlFilePathAndTitle)
        #change the path and the kindlegen file to your path c2 is Kindle Hight Compression
        cmd = realPath+('/KindleGen %s -c1' % opfPath)
        print cmd
        subprocess.call(cmd, shell=True)
        mobifilePath.append(os.path.splitext(opfPath)[0]+".mobi")
        #clean tmp files
        self._cleanTmpFiles(htmlFilePathAndTitle,tocHtmlPath,tocNcxPath,opfPath)
        return mobifilePath

    def _cleanTmpFiles(self,htmlFilePathAndTitle,tocHtmlPath,tocNcxPath,opfPath):
        os.unlink(tocHtmlPath)
        os.unlink(tocNcxPath)
        os.unlink(opfPath)
        for fileAndTitle in htmlFilePathAndTitle:
            os.unlink(fileAndTitle[0])

    def make_content_html(self,txtfilenames):
        htmlFilePathAndTitle=[]
        for path in txtfilenames:
            fp = open(path, "r")
            htmlPath=os.path.splitext(path)[0]+".html"
            htmlFiles=open(htmlPath,"w")
            lines=fp.readlines()
            title="<html><head><meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\"><title>"+lines[0]+"</title></head><body>"
            htmlFiles.write(title)
            for line in lines:
                if not line.isspace():
                    htmlFiles.write("<p>"+line+"</p>");
            htmlFiles.write("</body></html>")
            htmlFiles.close()
            fileinfo=[htmlPath,lines[0]]
            htmlFilePathAndTitle.append(fileinfo)
        return htmlFilePathAndTitle

    def make_TOC_html(self,htmlFilePathAndTitle):
        #htmlFilePathAndTitle=[[path,title],[path,title].....]
        tocHeader='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Table of Contents</title>
</head>
<body>
<h1>目录</h1>
<hr width="80%" />
<p><br />'''
        tocContent=""
        for pathAndTitle in htmlFilePathAndTitle:
            tocContent+='<a href="%s">%s</a><br />'%(pathAndTitle[0],pathAndTitle[1])
        tocFooter="</p></body></html>"

        tochtml=tocHeader+tocContent+tocFooter
        filename=realPath+"/toc.html"
        ot_file=open(filename,'w')
        ot_file.write(tochtml)
        ot_file.close()
        return filename

    def make_TOC_ncx(self,htmlFilePathAndTitle,tocPath):
        #htmlFilePathAndTitle=[[path,title],[path,title].....]
        ncxHearder='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en-US">
<head>
<meta name="dtb:uid" content="BookId"/>
<meta name="dtb:depth" content="2"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>
<docTitle><text>%s</text></docTitle>
<docAuthor><text>%s</text></docAuthor>
<navMap>''' % (self.bookname,self.author)
        ncxtoc='''<navPoint class="toc" id="toc" playOrder="1">
        <navLabel><text>Table of Contents</text></navLabel>
        <content src="%s"/></navPoint>'''%(tocPath)
        ncxContent=""
        idNum=2;
        for pathAndTitle in htmlFilePathAndTitle:    
            ncxContent+='''<navPoint class="chapter" id="chapter%d" playOrder="%d">
            <navLabel><text>%s</text></navLabel>
            <content src="%s"/></navPoint>'''%(idNum,idNum,pathAndTitle[1],pathAndTitle[0])
            idNum+=1
        ncxFooter="</navMap></ncx></ncx>"

        ncx=ncxHearder+ncxtoc+ncxContent+ncxFooter
        filename=realPath+"/toc.ncx"
        ot_file=open(filename,'w')
        ot_file.write(ncx)
        ot_file.close()
        return filename

    def make_OPF(self,coverPath,tocNcxPath,tocHtmlPath,htmlFilePathAndTitle):
        today=time.strftime('%m%d%H%M',time.localtime(time.time()))
        if coverPath is None:
            coverPath="None"
        tagID=1
        htmlPathTag=''
        itemref=''
        for pathAndTitle in htmlFilePathAndTitle:
            htmlPathTag+='<item id="item%d" media-type="text/x-oeb1-document" href="%s"></item>'%(tagID,pathAndTitle[0])
            itemref+='<itemref idref="item%d"/>'%(tagID)
            tagID+=1

        opf='''<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
        <metadata>
                <dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
                        <dc:Title>%s%s</dc:Title>
                        <dc:Language>zh</dc:Language>
                        <dc:Identifier id="uid">010B5D2ACA</dc:Identifier>
                        <dc:Creator>作者:%s 生成工具:EzRead</dc:Creator>
                        <dc:Subject>小说</dc:Subject>
                </dc-metadata>
                <x-metadata>
                        <output encoding="utf-8"></output>
                        <EmbeddedCover>%s</EmbeddedCover>
                </x-metadata>
        </metadata>
        <manifest>
                <item id="My_Table_of_Contents" media-type="application/x-dtbncx+xml" href="%s"/>
                <item id="item0" media-type="application/xhtml+xml" href="%s"></item>
                %s
        </manifest>
        <spine toc="My_Table_of_Contents">
                <itemref idref="item0"/>
                %s
        </spine>
        <tours></tours>
        <guide>
                <reference type="toc" title="Table of Contents" href="%s"></reference>
        </guide>
</package>'''%(self.bookname,today,self.author,coverPath,tocNcxPath,tocHtmlPath,htmlPathTag,itemref,tocHtmlPath)

        filename=realPath+"/%s%s.opf"%(self.perfix,today)
        ot_file=open(filename,'w')
        ot_file.write(opf)
        ot_file.close()
        return filename

        
def main():
    '''Run the main program'''
    usage="%prog [options]"
    parser=OptionParser(usage)
    parser.add_option("-k","--kindlegen",action="store_true",dest="kindlegenBoolValue",
        help="Convert txt files to a mobi file with KindleGen")
    parser.add_option("-s","--sendtokindle",action="store_true",dest="sendBoolValue",
        help="Automatically send files to Your Kindle Email Address")
    (options,args)=parser.parse_args()
    if options.kindlegenBoolValue is True:
        print 'kindlegenBoolValue is open'
    if options.sendBoolValue is True:
        print 'sendBoolValue is open'
    try:
        GenTextFiles(options.kindlegenBoolValue,options.sendBoolValue)
    except KeyboardInterrupt as e:
        print >> sys.stderr, 'Program interrupted, exiting...'
        sys.exit(10)

if __name__ == '__main__':
        main()