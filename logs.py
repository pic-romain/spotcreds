import smtplib, json
import os, errno

def mkdir_p(path):
    """http://stackoverflow.com/a/600612/190597 (tzot)"""
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

class ERROR_EMAIL(object):
    def __init__(self):
        gmail_account = json.load(open('conf_gmail.json', 'r'))

        self.FROM     = gmail_account["email"]
        self.TO       = [gmail_account["send_to"]]
        self.PW
        
    def send(self,subject,content):
        server = smtplib.SMTP_SSL("smtp.gmail.com",465,context=None)
        server.login(self.FROM,self.PW)
        server.sendmail(self.FROM, self.TO, f"Subject: [Spotlight On The Credits] {subject}\n{content}")
        server.quit()
if __name__=="__main__":
    error_email = ERROR_EMAIL()
    error_email.send(subject='Testing function',content="Is this working?")