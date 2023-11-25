import os

def didMailBoxCreated():
    current_directory = os.getcwd()
    dirMailBox = current_directory + "\MailBox"

    lFolders = []
    lFolders.append(dirMailBox)
    lFolders.append(dirMailBox + "\Important")
    lFolders.append(dirMailBox + "\Inbox")
    lFolders.append(dirMailBox + "\Project")
    lFolders.append(dirMailBox + "\Spam")
    lFolders.append(dirMailBox + "\Work")

    for folder in lFolders:
        if not os.path.exists(folder):
            os.makedirs(folder)