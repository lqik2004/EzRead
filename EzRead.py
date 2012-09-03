#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
EzRead can fetch WebPage content with aweasome layout and send it to your kindle automatically
Now it only fit for 《武动乾坤》,a popular fiction on Qidian.com
if you like this fiction, you can download and use EzRead immediately.

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
import optparse
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

_version = '1'

####################SENDTOKINDLE####################
class SendKindle:
    conffile='./sendkindle.cfg'
    sample_conf='''  [Default]
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
            self.smtp_server = config.get('Default', 'smtp_server')
            self.smtp_port = config.getint('Default', 'smtp_port')
            self.smtp_login = config.get('Default', 'smtp_login')
            self.user_email = config.get('Default', 'user_email')
            self.kindle_email = config.get('Default', 'kindle_email')
            self.smtp_password =config.get('Default', 'smtp_password')
            self.convert = config.getboolean('Default', 'convert')
        except (IOError, ConfigParser.Error, ValueError) as e:
            print e
            message = "You're missing a program configuration file. Please " \
                      "create %s with the following example content:\n" \
                      "%s" % (self.conffile, self.sample_conf)
            print >> sys.stderr, message
            sys.exit(3)

    def send_mail(self,files):
        '''Send email with attachments'''

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
    def __init__(self):
        super(GenTextFiles, self).__init__()
        self.filenames=[]

        lasturl=open("lasturl.txt").read()
        url=lasturl
        #Doc Number--I could not use chinese char in file title...help me ,pls.
        pg=re.search(r'/([^.]*).html',url).group(1)
        fname="WDQK_"+pg+".txt"

        
        files = os.listdir(os.getcwd())  
        result=fname in files
        if result is False:
            #不存在
            self.genNewFile(url,pg)

        while self.searchNextURL(url) is True :
            lasturl=open("lasturl.txt").read()
            url=lasturl
            #Doc Number--I could not use chinese char in file title...help me ,pls.
            pg=re.search(r'/([^.]*).html',url).group(1)
            self.genNewFile(url,pg)
        
        #send files to kindle
        kindle = SendKindle()
        kindle.send_mail(self.filenames)
        
    def searchNextURL(self,currenturl):
        req = urllib.urlopen(currenturl)
        text = req.read()
        try:
            nexturl=re.search(r"<a\s*id=\"xiayipian\"\s*class=\"r\"\s*href=\"([^\"]*)",text)
            if nexturl is not None:
                nexturl=nexturl.group(1)
        finally:
            pass

        if nexturl is not None:
            wirte_lastURlFile=codecs.open("lasturl.txt","w",'utf-8')
            wirte_lastURlFile.write(nexturl)
            wirte_lastURlFile.close()
            #print nexturl
            return True
         
    def genNewFile(self,url,pg): 
        req = urllib.urlopen(url)
        text = req.read()
        #title
        title=re.search(r'<H1>([^<]*)</H1>',text).group(1)
        title="《武动乾坤》"+title
        title=title.decode("utf-8")
        #print title
        
        text=re.search(r'<div class="content-body">[\s\S]*<div style="clear:both">', text).group()    
        encoding = _getCharacterEncoding(req.headers, text)[0]
        if encoding == 'us-ascii': encoding = 'utf-8'
        try:
            text = text.decode(encoding)
        except UnicodeDecodeError:
            text = text.decode(chardet.detect(text)['encoding'])            
        output=html2text.HTML2Text()
        output.ignore_links=True
        ot_string=output.handle(text)
        ot_string=title+"\n"+ot_string+u"\n感谢使用本书的自动生成工具EzRead\n作者：lqik2004#gmail.com\nTwitter:@lqik2004"
        filename="WDQK_"+pg+".txt"
        ot_file=codecs.open(filename,'w','utf-8')
        ot_file.write(ot_string)
        ot_file.close()
        self.filenames.append(filename)



def main():
    '''Run the main program'''
    try:
        GenTextFiles()
    except KeyboardInterrupt as e:
        print >> sys.stderr, 'Program interrupted, exiting...'
        sys.exit(10)

if __name__ == '__main__':
        main()