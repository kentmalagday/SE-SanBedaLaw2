import smtplib
from email.message import EmailMessage

class Mail:
    def __init__(self, userData, articleData=None, body=None, subject=None):
        self.gmail_user = 'nall.ngo.try@gmail.com'
        self.gmail_password = 'cmprebezdanlnjmd'
        self.sent_from = self.gmail_user
        self.cc = userData['email']
        if articleData is not None:
            self.to = articleData['authorEmail']
        else:
            self.to = self.gmail_user
        if subject is None:
            self.subject = "Request Access for {}".format(articleData['articleTitle'])
        else:
            self.subject = subject
        if body is None:
            self.body = """
I am {} from {}, with the help of Network of Academic Law Librarians,Inc., 
is asking kindly for an Access in a {}, titled {}, for the purpose of using it as a 
reference material in a study that I am currently conducting. Thank you for taking the time to read this email 
and for your kind consideration.

Yours truly,
{}
{}""".format(userData['fullName'], userData['institution'], articleData['pubType'], articleData['articleTitle'], userData['fullName'], userData['email'])
        else:
            self.body = body

        
    def sendMail(self):
        try:
            msg = EmailMessage()
            msg.set_content(self.body)
            msg['Subject'] = self.subject
            msg['From'] = self.gmail_user
            msg['To'] = self.to
            msg['Cc'] = self.cc
            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com',465)
            smtp_server.ehlo()
            smtp_server.login(self.gmail_user,self.gmail_password)
            smtp_server.send_message(msg)
            smtp_server.close()
            return("Success")
        except Exception as ex:
            return ("Error: ", ex)


