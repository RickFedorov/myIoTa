from psw import mail_psw, mail_user, mail_adm
from imbox import Imbox
import json
from logs.logger import logger
import time
from simplesmtp import SimpleSMTP


class Email2Mqtt():

    def __init__(self, client):
        self.client = client

    def check_mailbox(self):
        try:
            with Imbox("imap.seznam.cz",
                       username=mail_user,
                       password=mail_psw,
                       ssl=True,
                       ssl_context=None,
                       starttls=False) as imbox:
                messages = imbox.messages(folder='INBOX', unread=True)
                for uid, message in messages:
                    topic = message.subject
                    payload = json.loads(message.body["plain"][0])
                    try:
                        self.client.publish(topic, json.dumps(payload))
                    except:
                        logger.exception(" {} - Exception occurred...".format(message.subject))
                        continue

                    imbox.mark_seen(uid)  # command execuded
                else:
                    logger.info("No new message")
        except:
            logger.exception(" {} - Exception occurred...".format(mail_user))

    def run(self, name):
        while True:
            self.check_mailbox()
            time.sleep(10)


class Mqtt2Email():
    def __init__(self, client):
        self.client = client
        try:
            self.email = SimpleSMTP(
                host='smtp.seznam.cz',
                username=mail_user,
                passw=mail_psw,
                port=465,
                use_ssl=True,
                from_email=mail_user
            )
        except:
            logger.exception("Simple SMTP - Exception occurred...")


    def send_mail(self, subject, contents):
        try:
            self.email.send(to_email=mail_adm, subject=subject, email_message=contents)
        except:
            logger.exception(" {} - Exception occurred...".format(subject))