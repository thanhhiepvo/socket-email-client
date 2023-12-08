import reading_email

def getChoiceNumber(min, max):
    choice = int(input())
    while choice not in range(min, max + 1):
        choice = int(input("Chọn lại: "))
    return choice

def printClientConsole():
    print("Vui lòng chọn Menu")
    print("1. Để gửi email")
    print("2. Để xem danh sách các email đã nhận")
    print("3. Setting")
    print("4. Thoát")

    print("Bạn chọn: ", end="")
    choice = getChoiceNumber(1, 4)

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

    print("Có gửi kèm file (1. Có, 2. Không)")

    willSendFile = getChoiceNumber(1, 2)

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

    return buffer

def printReceivedEmailList(email):

    def getTheBoxName(choice_Mailbox):
        mail_box_list = ['Inbox', 'Project', 'Important', 'Work', 'Spam']
        return mail_box_list[choice_Mailbox - 1]

    data = reading_email.read_manage_json(email)
    while True:
        print("Đây là danh sách các folder trong mailbox của bạn:")
        print("1. Inbox")
        print("2. Project")
        print("3. Important")
        print("4. Work")
        print("5. Spam")
        print("6. EXIT")

        print("Bạn muốn xem mail trong folder nào: ", end="")
        choice_Mailbox = getChoiceNumber(1, 6)

        if choice_Mailbox == 6:
            return

        choice_Mailbox = getTheBoxName(choice_Mailbox)
        box_data = reading_email.get_mail_in_box(data, choice_Mailbox)
        
        print_emails_in_box(box_data, email, choice_Mailbox)

def print_emails_in_box(box_data, email, choice_Mailbox):
    def getTheDemandOnFilter(filter_based):
        while True:
            print()
            if not filter_based['sender_email']:
                print("1. Lọc email dựa trên địa chỉ người gửi")
            if not filter_based['subject']:
                print("2. Lọc email dựa trên subject")
            if not filter_based['content']:
                print("3. Lọc dựa trên content")
            print("4. Chọn lại")
            print("5. Không")
            print("Chọn số: ", end="")
            choice_number = getChoiceNumber(1, 5)

            if choice_number == 5:
                return filter_based
            elif choice_number == 4:
                filter_based['sender_email'] = False
                filter_based['subject'] = False
                filter_based['content'] = False
            elif choice_number == 1:
                filter_based['sender_email'] = True
            elif choice_number == 2:
                filter_based['subject'] = True
            else:
                filter_based['content'] = True
            
    reading_email.print_mails_into_console(box_data)

    # map-check for filling
    filter_based = dict()
    filter_based['sender_email'] = False
    filter_based['subject'] = False
    filter_based['content'] = False
    filter_based = getTheDemandOnFilter(filter_based)

    filter_data = fillMails(box_data, filter_based)
    
    nLetters = len(filter_data)

    while True:
        if nLetters == 0:
            print("Không có email nào")
        else:
            print("0. Kích hoạt tính năng chuyển mail sang thư mục khác")
            reading_email.print_mails_into_console(filter_data)
        print(nLetters + 1, "EXIT")

        choice_file = getChoiceNumber(0, nLetters + 1)

        if choice_file == nLetters + 1:
            break

        if choice_file == 0:
            moved_file = getTheMovedFile(filter_data, nLetters)

            if moved_file == None:
                continue
            
            the_mail = filter_data[moved_file - 1]
            des_box = choice_destinate_folder(the_mail)

            filter_data.remove(the_mail)
            nLetters -= 1
            
            reading_email.moveFile(email, the_mail, des_box)
            continue

        print()
        print("The content in this mail:")
        print(reading_email.print_mail_content(box_data, choice_file, email, choice_Mailbox))

        reading_email.markFileWasRead(email, box_data[choice_file - 1]['subject'])
        input("Press Enter to continue...")

def choice_destinate_folder(the_mail):
    sub_box = ['Inbox', 'Project', 'Important', 'Work', 'Spam']
    source_folder = the_mail['box']

    sub_box.remove(source_folder)
    print(sub_box)
    count = 1
    for item in sub_box:
        print(count, ".", item)
        count += 1
    print("Choice the destination folder: ", end="")
    choice_number = getChoiceNumber(1, 5)
    return sub_box[choice_number - 1]

def fillMails(filter_data, filter_based):
    if filter_based['sender_email']:
        filter_data = fill_emails_based_sender_email(filter_data)
    if filter_based['subject']:
        filter_data = fill_emails_based_subject(filter_data)

    return filter_data

def getTheMovedFile(filter_data, nLetters):
    reading_email.print_mails_into_console(filter_data)
    print("Choose the file you want to move: ", end="")
    choice_number = getChoiceNumber(1, nLetters + 1)

    if choice_number == nLetters:
        return None
    return choice_number

def fill_emails_based_subject(data):
    anything = str(input("Enter the thing you want to fill the subject: "))
    anything = anything.upper()
    final_data = []
    for item in data:
        subject = item['subject'].upper()
        if anything in subject:
            final_data.append(item)
    return final_data

def fill_emails_based_sender_email(data):
    
    def get_the_email_will_be_filled(sender_email):
        for email in sender_email:
            print(email)
        enter_email = str(input("Enter an email above: "))
        while enter_email not in sender_email:
            print("This email you recent entered is not exist")
            enter_email = str(input("Enter again: "))
        return enter_email.strip()

    sender_email = set()
    for item in data:
        sender_email.add(item['sender_email'])

    the_email = get_the_email_will_be_filled(sender_email)
    final_data = []
    for item in data:
        if item['sender_email'] == the_email:
            final_data.append(item)
    
    return final_data