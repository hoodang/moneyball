import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


from email import encoders


def send_mail(send_from, send_to, subject, text, f, server="localhost"):
    assert type(send_to) == list
    # assert type(files) == list

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    # for f in files:
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(f, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
    msg.attach(part)
    # smtp = smtplib.SMTP(server)
    # smtp.sendmail(send_from, send_to, msg.as_string())
    # smtp.close()


    # fromaddr = 'lancecreath@gmail.com'
    # toaddr = send_to
    #
    # msg = MIMEMultipart()
    #
    # msg['From'] = fromaddr
    # msg['To'] = toaddr
    # msg['Subject'] = subject
    #
    # body = text
    #
    # msg.attach(MIMEText(body, 'plain'))
    #
    # filename = "NAME OF THE FILE WITH ITS EXTENSION"
    # attachment = open("PATH OF THE FILE", "rb")
    #
    # part = MIMEBase('application', 'octet-stream')
    # part.set_payload((attachment).read())
    # encoders.encode_base64(part)
    # part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    #
    # msg.attach(part)
    #
    # smtp = smtplib.SMTP(server)
    # smtp.sendmail(send_from, send_to, msg.as_string())
    # smtp.close()
    #
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(send_from, 'j.79:iDc')
    text = msg.as_string()
    server.sendmail(send_from, send_to, text)
    server.quit()