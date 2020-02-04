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
from __future__ import print_function

import sys
import time
import datetime
import smtplib
import types
import re
import email.charset

from simplesmtp import util


class SimpleSMTP(object):
    """A simple class to send e-mails, plain text or html with attachments.
    The "attachments" keyword param for the method "send" is a list of dict:
    attachments = [
        {
            'file': path or a stream to file,
            'filename': the name of the file
        }
    ]
    """
    def __init__(self, host, username=None, passw=None, from_email=None, debug=False, port=25, use_ssl=False):
        self.smtp_host = host
        self.smtp_port = port
        self.use_ssl = use_ssl
        self.from_email = from_email
        self.set_auth(username, passw)
        self.debug = debug

    def set_auth(self, username, passw):
        self.smtp_username = username
        self.smtp_passwd = passw

    def _smtp_send(self, email_body, from_email=None, to_mail_str=None):
        result = True
        if to_mail_str:
            email_body.replace_header('To', to_mail_str)
        to_email = email_body['To'].strip().split(',')
        from_email = from_email or self.from_email
        try:
            smtp = None
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
            else:
                smtp = smtplib.SMTP(host=self.smtp_host, port=self.smtp_port)
            if self.debug:
                smtp.set_debuglevel(1);
            send_headers = ('Cc', 'Bcc')
            for k in email_body.keys():
                if k in send_headers:
                    to_email.append(email_body[k])
            if self.smtp_username:
                smtp.login(self.smtp_username, self.smtp_passwd)
            smtp.sendmail(from_email, to_email, email_body.as_string())
            smtp.quit()
            if self.debug:
                print('[DEBUG] Message')
                print(email_body.as_string())
        except:
            result = False
            if self.debug:
                raise
        return result

    def send(self, from_email=None, to_email=None, subject=None, email_message=None, email_body=None, msg_type='plain', alt_text='', headers={}, attachments=[], charset='utf-8'):
        if email_body is None:
            email_body = util.create_mime_mail(
                from_email=from_email or self.from_email,
                to_email=to_email,
                subject=subject,
                email_message=email_message,
                msg_type=msg_type,
                alternative_text=alt_text,
                headers=headers,
                attachments=attachments,
                charset=charset
            )
        return self._smtp_send(email_body=email_body, from_email=from_email, to_mail_str=to_email)
