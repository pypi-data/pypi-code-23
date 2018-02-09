#
# Copyright (c) 2018 by Ben Sommer. All Rights Reserved. Unauthorised distribution is NOT allowed.
#

import smtplib
from firebase import firebase
def send_gmail(youremail, yourpassword, to, subject, body, database):
    try:
        boxport = 25
        boxaddress = "smtp.gmail.com"

        # config
        smtpObj = smtplib.SMTP(boxaddress, boxport)
        smtpObj.starttls()
        smtpObj.ehlo()

        # log in
        smtpObj.login(str(youremail), str(yourpassword))

        # send
        smtpObj.sendmail(str(youremail), str(to), (("From:" + str(youremail) + "\n") + ("To:" + str(to) + "\n") + ("Subject:" + str(subject)) + "\n" + (body)))
        if database != None:
            sentby, b = youremail.split("@")
            complete = ["'", (subject.title()), "'", " Sent by : ", sentby]
            sentmessagetext = "".join(complete)
            yourdata = firebase.FirebaseApplication(str(database))
            yourdata.put("/emails", sentmessagetext, body)
    except smtplib.SMTPAuthenticationError :
        # return Error
        print("Authentication Error : Could not connect to Gmail's servers. \n Try running the program again \n If the problem persists, check your username and password. \n You may need to enable Less Secure Apps for your Gmail Account")
    else:
        print("Sent Email to :", to)

def send_icloud(youremail, yourpassword, to, subject, body, database):
    try:
        boxport = 25
        boxaddress = "smtp.mail.me.com"

        # config
        smtpObj = smtplib.SMTP(boxaddress, boxport)
        smtpObj.ehlo()
        smtpObj.starttls()

        # log in
        smtpObj.login(str(youremail), str(yourpassword))

        # send
        smtpObj.sendmail(str(youremail), str(to), (("From:" + str(youremail) + "\n") + ("To:" + str(to) + "\n") + ("Subject:" + str(subject)) + "\n" + (body)))
        if database != None:
            sentby, b = youremail.split("@")
            complete = ["'", (subject.title()), "'", " Sent by : ", sentby]
            sentmessagetext = "".join(complete)
            yourdata = firebase.FirebaseApplication(str(database))
            yourdata.put("/emails", sentmessagetext, body)
    except smtplib.SMTPAuthenticationError :
        # return Error
        print("Authentication Error : Could not connect to Gmail's servers. \n Try running the program again \n If the problem persists, check your username and password. \n You may need to enable Less Secure Apps for your Gmail Account")
    else:
        print("Sent Email to :", to)

def send_yahoo(youremail, yourpassword, to, subject, body, database):
    try:
        boxport = 25
        boxaddress = "smtp.mail.yahoo.com"

        # config
        smtpObj = smtplib.SMTP(boxaddress, boxport)
        smtpObj.ehlo()
        smtpObj.starttls()

        # log in
        smtpObj.login(str(youremail), str(yourpassword))

        # send
        smtpObj.sendmail(str(youremail), str(to), (("From:" + str(youremail) + "\n") + ("To:" + str(to) + "\n") + ("Subject:" + str(subject)) + "\n" + (body)))
        if database != None:
            sentby, b = youremail.split("@")
            complete = ["'", (subject.title()), "'", " Sent by : ", sentby]
            sentmessagetext = "".join(complete)
            yourdata = firebase.FirebaseApplication(str(database))
            yourdata.put("/emails", sentmessagetext, body)
    except smtplib.SMTPAuthenticationError :
        # return Error
        print("Authentication Error : Could not connect to Gmail's servers. \n Try running the program again \n If the problem persists, check your username and password. \n You may need to enable Less Secure Apps for your Gmail Account")
    else:
        print("Sent Email to :", to)

def send_custom(port, smtpserver, youremail, yourpassword, to, subject, body, database):
    try:
        if port != None:
            boxport = int(port)
        else:
            boxport = 25
        boxaddress = string(smtpserver)

        # config
        smtpObj = smtplib.SMTP(boxaddress, boxport)
        smtpObj.ehlo()
        smtpObj.starttls()

        # log in
        smtpObj.login(str(youremail), str(yourpassword))

        # send
        smtpObj.sendmail(str(youremail), str(to), (("From:" + str(youremail) + "\n") + ("To:" + str(to) + "\n") + ("Subject:" + str(subject)) + "\n" + (body)))
        if database != None:
            sentby, b = youremail.split("@")
            complete = ["'", (subject.title()), "'", " Sent by : ", sentby]
            sentmessagetext = "".join(complete)
            yourdata = firebase.FirebaseApplication(str(database))
            yourdata.put("/emails", sentmessagetext, body)
    except smtplib.SMTPAuthenticationError :
        # return Error
        print("Authentication Error : Could not connect to Gmail's servers. \n Try running the program again \n If the problem persists, check your username and password. \n You may need to enable Less Secure Apps for your Gmail Account")
    else:
        print("Sent Email to :", to)

def email_list(username, password, databaseurl, mode, findoutmoreurl, subject, whofrom):
    import easyemailer as ee
    from firebase import firebase
    firebaseok = []
    fb = firebase.FirebaseApplication(databaseurl)
    data = fb.get("/listofcontacts", None)
    del data[0]

    if "version-" in mode:
        version = mode.replace("version-", "")
        notification = ("notify you about the new version : " + version)
    elif "confirm-" in mode:
        confirmation = mode.replace("confirm-", "")
        notification = ("confirm" + confirmation)
    else:
        print("Please use a correct mode.")

    textstuffs = "Dear Sir/Madam ," + "\n" + "\n" + "We would like to " + notification + ". \n" + "To find out more, visit " + findoutmoreurl + " . \n Thank you for your time, \n " + whofrom

    for item in data:
        newstuff = item.replace( "_A_", "@")
        neweststuff = newstuff.replace( "_D_", ".")
        ee.send_gmail(str(username), str(password), neweststuff, subject, textstuffs, None)
