# Copyright 2019, Anderson R. Livramento. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import time
import datetime
import types
import re
import base64

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

US_WEEK = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
US_MONTH = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
EMBDD_IMG_SRC = re.compile(r'<img.*?src="data:(.*?)"', re.S | re.M)


def calc_timezone():
    dec_time = time.timezone / 3600
    if time.localtime().tm_isdst:
        dec_time -= 1
    return dec_time


def rfc_date():
    today = datetime.datetime.now()
    dec_time = calc_timezone()
    #format()
    mail_date_str = today.strftime('{0}, %d {1} %Y %H:%M:%S -{2}')
    week_day = US_WEEK[today.weekday()]
    month = US_MONTH[today.month - 1]
    return mail_date_str.format(week_day, month, str(dec_time).rjust(2,'0').ljust(4,'0'))


def _uri_data_mediatype(s):
    if s:
        i = s.find(';')
        if i > -1:
            return s[:i]
    return ''


def has_embedded_img(html_src):
    common_imgs_mediatypes = {
        'image/png': 'png',
        'image/jpg': 'jpg',
        'image/jpeg': 'jpg',
        'image/svg+xml': 'svg'
    }
    imgs = EMBDD_IMG_SRC.findall(html_src)
    mime_result = []
    if imgs:
        i = 0
        for ib in imgs:
            cid = 'img{0}'.format(i)
            sb64 = ib[ib.find(',') + 1:]
            # TODO: better way to extract extension
            mediatype = _uri_data_mediatype(ib)
            ext = ''
            if mediatype in common_imgs_mediatypes:
                ext = common_imgs_mediatypes[mediatype]
            html_src = html_src.replace(''.join(['data:', ib]), 'cid:{}'.format(cid))
            mime_img = MIMEImage(base64.b64decode(sb64))
            mime_img.add_header('Content-ID', '<{0}>'.format(cid))
            mime_img.add_header('Content-Disposition', 'inline', filename='{0}.{1}'.format(cid, ext))
            mime_result.append(mime_img)
            i += 1
    return (html_src, mime_result)


def create_mime_mail(from_email, to_email, email_message, msg_type='plain', subject=None, alternative_text=None, charset='utf-8', headers={}, attachments=[]):
    mime_mail_message  = None
    if msg_type == 'plain':
        mime_mail_message  = MIMEMultipart('mixed')
        mime_mail_message['Subject'] = subject
        mime_mail_message['From'] = from_email
        mime_mail_message['To'] = to_email
        mime_mail_message['Date'] = rfc_date()
        if headers:
            for k in headers:
                mime_mail_message[k] = headers[k]
        plain_message = MIMEText(email_message.encode(charset), 'plain', charset)
        mime_mail_message.attach(plain_message)
    elif msg_type == 'html':
        plaintext = alternative_text or 'Your e-mail client doesn\'t support HTML messages!'
        multipart_type = 'alternative'
        # First, scan for embedded images and create the appropriate mime type
        htmltext, mime_images = has_embedded_img(email_message)
        mime_alternative = None
        if mime_images:
            multipart_type = 'related'
            mime_alternative = MIMEMultipart('alternative')
        mime_mail_message = MIMEMultipart(multipart_type)
        mime_mail_message['Subject'] = subject
        mime_mail_message['From'] = from_email
        mime_mail_message['To'] = to_email
        mime_mail_message['Date'] = rfc_date()
        mime_mail_message.preamble = 'This is a multi-part message in MIME format.'
        if headers:
            for k in headers:
                mime_mail_message[k] = headers[k]
        # HTML text
        html_msg = MIMEText(htmltext.encode(charset), 'html', charset)
        # Plain text
        plain_msg = MIMEText(plaintext.encode(charset), 'plain', charset)
        if mime_alternative:
            mime_mail_message.attach(mime_alternative)
            mime_alternative.attach(plain_msg)
            mime_alternative.attach(html_msg)
            for img in mime_images:
                mime_mail_message.attach(img)
        else:
            mime_mail_message.attach(plain_msg)
            mime_mail_message.attach(html_msg)
    if mime_mail_message and attachments:
        # has attachments?
        if isinstance(attachments, types.ListType):
            for attach in attachments:
                attach_file = MIMEBase('application', 'octet-stream', name=attach.get('filename'))
                if isinstance(attach.get('file'), basestring):
                    fp = open(attach['file'], 'rb')
                    attach_file.set_payload(fp.read())
                    fp.close()
                else:
                    attach_file.set_payload(attach['file'].read())
                encoders.encode_base64(attach_file)
                attach_file.add_header('Content-Disposition', 'attachment', filename=attach.get('filename'))
                mime_mail_message.attach(attach_file)
    return mime_mail_message
