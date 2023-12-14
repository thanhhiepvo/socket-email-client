import reading_email
import subprocess
import platform
import os


def get_choice_number(min, max):
    choice = int(input())
    while choice not in range(min, max + 1):
        choice = int(input("Chọn lại: "))
    return choice


def print_client_console():
    print("Vui lòng chọn Menu")
    print("1. Để gửi email")
    print("2. Để xem danh sách các email đã nhận")
    print("3. Setting")
    print("4. Thoát")

    print("Bạn chọn: ", end="")
    choice = get_choice_number(1, 4)

    return choice


def print_sending_email():
    print("Đây là thông tin soạn email: ", end="")
    print(
        '(Các email cách nhau bằng dấu "," nếu không điền vui lòng nhấn enter để bỏ qua)'
    )

    recievers_To = str(input("To: "))
    recievers_To = recievers_To.split(",")
    recievers_To = [email.strip() for email in recievers_To]

    recievers_CC = str(input("CC: "))
    recievers_CC = recievers_CC.split(",")
    recievers_CC = [email.strip() for email in recievers_CC]

    recievers_BCC = str(input("BCC: "))
    recievers_BCC = recievers_BCC.split(",")
    recievers_BCC = [email.strip() for email in recievers_BCC]

    subject = str(input("Subject: "))
    print('Content (Khi muốn kết thúc việc nhập content hãy viết một dòng chỉ có "."):')
    content = ""
    line = ""
    while True:
        if line != ".":
            line = input()
            if line != ".":
                content = content + line + "\n"
        else:
            break

    willSendFile = int(input("Có gửi kèm file (1. Có, 2. Không): "))
    filePaths = []
    if willSendFile == 1:
        nFiles = int(input("Số lượng file muốn gửi: "))
        while nFiles < 0:
            nFiles = int(input("Nhập lại: "))

        for i in range(0, nFiles):
            path = str(input(f"Cho biết đường dẫn file thứ {i + 1}: "))
            filePaths.append(path)

    buffer = dict()
    buffer["To"] = recievers_To
    buffer["CC"] = recievers_CC
    buffer["BCC"] = recievers_BCC
    buffer["subject"] = subject
    buffer["content"] = content
    buffer["filePaths"] = filePaths

    return buffer


def check_email_existence(email):
    file_path = "./Mailbox/" + email + "/manage.json"
    return os.path.exists(file_path)


def print_received_email_list(email):
    def get_the_box_name(choice_Mailbox):
        mail_box_list = ["Inbox", "Project", "Important", "Work", "Spam"]
        return mail_box_list[choice_Mailbox - 1]

    if not check_email_existence(email):
        print("Email trong setting không tồn tại trong Mailbox của server!!")
        input("Nhấn enter để trở lại menu!!")
        return

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
        choice_Mailbox = get_choice_number(1, 6)

        if choice_Mailbox == 6:
            return

        choice_Mailbox = get_the_box_name(choice_Mailbox)
        box_data = reading_email.get_mail_in_box(data, choice_Mailbox)

        print_emails_in_box(box_data, email, choice_Mailbox)


def print_emails_in_box(box_data, email, choice_Mailbox):
    def find_mail_index_in_box_data(mail, box_data):
        for i in range(len(box_data)):
            if box_data[i] == mail:
                return i
        return None

    def get_the_demand_on_filter(filter_based):
        while True:
            print()
            if not filter_based["sender_email"]:
                print("1. Lọc email dựa trên địa chỉ người gửi")
            if not filter_based["subject"]:
                print("2. Lọc email dựa trên subject")
            if not filter_based["content"]:
                print("3. Lọc dựa trên content")
            print("4. Chọn lại")
            print("5. Không")
            print("Chọn số: ", end="")
            choice_number = get_choice_number(1, 5)

            if choice_number == 5:
                return filter_based
            elif choice_number == 4:
                filter_based["sender_email"] = False
                filter_based["subject"] = False
                filter_based["content"] = False
            elif choice_number == 1:
                filter_based["sender_email"] = True
            elif choice_number == 2:
                filter_based["subject"] = True
            else:
                filter_based["content"] = True

    reading_email.print_mails_into_console(box_data)

    # map-check for filling
    filter_based = dict()
    filter_based["sender_email"] = False
    filter_based["subject"] = False
    filter_based["content"] = False
    filter_based = get_the_demand_on_filter(filter_based)

    filter_data = fill_mails(box_data, filter_based, email, choice_Mailbox)

    nLetters = len(filter_data)

    while True:
        if nLetters == 0:
            print("Không có email nào")
        else:
            print("0. Kích hoạt tính năng chuyển mail sang thư mục khác")
            reading_email.print_mails_into_console(filter_data)
        print(nLetters + 1, "EXIT")

        choice_file_in_filter_data = get_choice_number(0, nLetters + 1)

        if choice_file_in_filter_data == nLetters + 1:
            break

        if choice_file_in_filter_data == 0:
            moved_file = get_the_moved_file(filter_data, nLetters)

            if moved_file == None:
                continue

            the_mail = filter_data[moved_file - 1]
            des_box = choice_destinate_folder(the_mail)

            filter_data.remove(the_mail)
            nLetters -= 1

            reading_email.move_file(email, the_mail, des_box)
            continue

        choice_file_in_filter_data -= 1  # because index in list count from 0

        print()
        print("Nội dung trong email:")
        email_card = filter_data[choice_file_in_filter_data]
        choice_file_in_box_data = find_mail_index_in_box_data(email_card, box_data)
        print(
            reading_email.get_mail_content(
                box_data, choice_file_in_filter_data, email, choice_Mailbox
            )
        )

        reading_email.mark_file_was_read_on_disk(
            email, box_data[choice_file_in_box_data]
        )
        filter_data[choice_file_in_filter_data]["read"] = "Yes"
        box_data[choice_file_in_box_data]["read"] = "Yes"

        # open file attachment if having
        if email_card["attachment"] == True:
            file_folder = (
                os.getcwd()
                + "\Mailbox\\"
                + email
                + "\\"
                + email_card["box"]
                + "\\"
                + email_card["subject"]
                + "\\"
            )
            file_name = reading_email.get_file_name_in_folder(file_folder)
            file_directory = file_folder + file_name
            print("direc:", file_directory)

            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.call(["open", file_directory])  # MacOS
                elif system == "Darwin":
                    subprocess.call(["start", file_directory], shell=True)  # Windows
                else:
                    print("Hệ điều hành không xác định, không thể mở file đính kèm")
            except Exception as e:
                print(f"Lỗi: {e}")

        input("Ấn Enter để tiếp tục...")


def choice_destinate_folder(the_mail):
    sub_box = ["Inbox", "Project", "Important", "Work", "Spam"]
    source_folder = the_mail["box"]

    sub_box.remove(source_folder)
    print(sub_box)
    count = 1
    for item in sub_box:
        print(count, ".", item)
        count += 1
    print("Chọn thư mục để lưu: ", end="")
    choice_number = get_choice_number(1, 5)
    return sub_box[choice_number - 1]


def fill_mails(filter_data, filter_based, email, sub_box):
    if filter_based["sender_email"]:
        filter_data = fill_emails_based_sender_email(filter_data)
    if filter_based["subject"]:
        filter_data = fill_emails_based_subject(filter_data)
    if filter_based["content"]:
        filter_data = fill_emails_based_content(filter_data, email, sub_box)

    return filter_data


def get_the_moved_file(filter_data, nLetters):
    reading_email.print_mails_into_console(filter_data)
    print("Chọn file bạn muốn di chuyển: ", end="")
    choice_number = get_choice_number(1, nLetters + 1)

    if choice_number == nLetters:
        return None
    return choice_number


def fill_emails_based_content(data, email, sub_box):
    anything = str(input("Nhập nội dung: "))
    anything = anything.upper()
    final_data = []
    for i in range(len(data)):
        email_content = reading_email.get_mail_content(data, i + 1, email, sub_box)
        email_content = email_content.upper()
        if anything in email_content:
            final_data.append(data[i])
    return final_data


def fill_emails_based_subject(data):
    anything = str(input("Nhập tiêu đề: "))
    anything = anything.upper()
    final_data = []
    for item in data:
        subject = item["subject"].upper()
        if anything in subject:
            final_data.append(item)
    return final_data


def fill_emails_based_sender_email(data):
    def get_the_email_will_be_filled(sender_email):
        for email in sender_email:
            print(email)
        enter_email = str(input("Chọn một email: "))
        while enter_email not in sender_email:
            print("Email bạn vừa nhập không tồn tại")
            enter_email = str(input("Enter again: "))
        return enter_email.strip()

    sender_email = set()
    for item in data:
        sender_email.add(item["sender_email"])

    the_email = get_the_email_will_be_filled(sender_email)
    final_data = []
    for item in data:
        if item["sender_email"] == the_email:
            final_data.append(item)

    return final_data
