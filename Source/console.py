def printClientConsole():
    print("Vui lòng chọn Menu")
    print("1. Để gửi email")
    print("2. Để xem danh sách các email đã nhận")
    print("3. Thoát")
    choice = int(input("Bạn chọn:"))
    while choice not in [1, 2, 3]:
        choice = int(input("Chọn lại:"))

    return choice

def printSendingEmail():
    print("Đây là thông tin soạn email: ", end="")
    print("(nếu không điền vui lòng nhấn enter để bỏ qua)")

    recievers_To = str(input("To: "))
    recievers_To = recievers_To.split(',')
    recievers_To = [email.strip() for email in recievers_To]
    
    recievers_CC = str(input("CC: "))
    recievers_CC = recievers_CC.split(',')
    recievers_CC = [email.strip() for email in recievers_CC]

    recievers_BCC = str(input("BCC: "))
    recievers_BCC = recievers_BCC.split(',')
    recievers_BCC = [email.strip() for email in recievers_BCC]

    subject = str(input("Subject: "))
    content = str(input("Content: "))

    willSendFile = int(input("Có gửi kèm file (1. Có, 2. Không)"))
    while willSendFile not in [1, 2]:
        willSendFile = int(input("Nhập lại: "))

    filePaths = []
    if willSendFile == 1:
        nFiles = int(input("Số lượng file muốn gửi: "))
        while nFiles < 0:
            nFiles = int(input("Nhập lại: "))

        for i in range(0, nFiles):
            path = str(input("Cho biết đường dẫn file thứ", i + 1))
            filePaths.append(path)
    
    buffer = dict()
    buffer['To'] = recievers_To
    buffer['CC'] = recievers_CC
    buffer['BCC'] = recievers_BCC
    buffer['subject'] = subject
    buffer['content'] = content
    buffer['filePaths'] = filePaths

    #return recievers, subject, content, nFiles, filePaths
    return buffer

def printReceivedEmailList():
    print("Đây là danh sách các folder trong mailbox của bạn:")
    print("1. Inbox")
    print("2. Project")
    print("3. Important")
    print("4. Work")
    print("5. Spam")
    nMailbox = int(input("Bạn muốn xem email trong folder nào: "))
    print("Nhấn enter để thoát ra ngoài")
    
    return nMailbox