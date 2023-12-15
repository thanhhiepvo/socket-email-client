import os
import email
from email.header import decode_header
import socket
import json

from download_email import ClientConfig
from download_email import EmailFilter
from download_email import EmailDownloader

import base64


class EmailReader:
    def __init__(self, client_config):
        self.client_config = client_config
        self.state_folder = "State"
        self.state_filename = f"{self.client_config.email}.txt"
        self.state_filepath = os.path.join(self.state_folder, self.state_filename)
        self.downloaded_emails = self.load_state()
        self.read_emails = self.load_state()
        if not os.path.exists(self.state_folder):
            os.makedirs(self.state_folder)

    def save_state(self, state):
        with open(self.state_filepath, "w") as state_file:
            state_file.write(",".join(map(str, state)))

    def load_state(self):
        if os.path.exists(self.state_filepath):
            with open(self.state_filepath, "r") as state_file:
                state_content = state_file.read().strip()

                if state_content:
                    return set(map(int, state_content.split(",")))
                else:
                    return set()
        else:
            return set()

    def should_save_to_folder(self, email_content, flags):
        for flag in flags:
            if flag in email_content:
                return True
        return False

    def save_mail_content(self, subject, email_content):
        email_content = email_content.replace("\r\n", "\n")
        mailbox_path = "./Mailbox/" + self.client_config.email
        if not os.path.exists(mailbox_path):
            os.makedirs(mailbox_path)
        saved = False

        for filter in self.client_config.filters:
            if self.should_save_to_folder(email_content, filter.flags):
                filter_folder = os.path.join(mailbox_path, filter.folder)
                if not os.path.exists(filter_folder):
                    os.makedirs(filter_folder)

                filename = f"{filter_folder}/{subject}.msg"
                with open(filename, "w") as file:
                    file.write(email_content)
                saved = True

        if not saved:
            filter_folder = os.path.join(mailbox_path, "./Inbox")
            if not os.path.exists(filter_folder):
                os.makedirs(filter_folder)
            filename = f"{filter_folder}/{subject}.msg"
            with open(filename, "w") as file:
                file.write(email_content)

    def load_email_to_managing(
        self, subject, sender_email, sender_name, attachment=False
    ):
        folder_box = "./Mailbox/" + self.client_config.email
        file_manage = folder_box + "/manage.json"

        if not os.path.exists(folder_box):
            os.makedirs(folder_box)

        data = []
        if os.path.exists(file_manage):
            f = open(file_manage)
            data = json.load(f)
            f.close()
            data = data["emails"]
        else:
            with open(file_manage, "w") as file:
                file.write("")

        new_mail = {
            "subject": subject,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "attachment": attachment,
            "box": "Inbox",
            "read": "No",
        }

        data.append(new_mail)
        json_data = {"emails": data}

        # print("A")
        with open(file_manage, "w") as file:
            json.dump(json_data, file, indent=4)

    def get_boundary(self, message):
        # Tìm vị trí của chuỗi "boundary="
        boundary_start = message.find("boundary=")

        # Kiểm tra xem "boundary=" có tồn tại trong chuỗi không
        if boundary_start == -1:
            return None

        # Tách phần sau "boundary=" để lấy giá trị boundary
        boundary_start += len("boundary=")
        boundary_end = message.find("\n", boundary_start)

        if boundary_end == -1:
            boundary_end = len(message)

        boundary_value = message[boundary_start:boundary_end].strip()

        # Xóa ký tự trống hoặc dấu nháy nếu có
        boundary_value = boundary_value.strip('"')
        boundary_value = boundary_value.strip("-")

        return boundary_value

    def split_message_by_boundary(self, message, boundary):
        # Tách message thành các phần dựa vào boundary
        parts = message.split(boundary)

        # Lọc các phần không cần thiết
        parts = [part.strip() for part in parts if part.strip()]

        if boundary == "boundary":
            return parts[2 : len(parts) - 1]

        return parts[1 : len(parts) - 1]

    def read_email(self, email_number):
        try:
            mail_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.client_config.mailserver, self.client_config.pop3)
            mail_socket.connect(server_address)
            response_user = mail_socket.recv(1024).decode()
            mail_socket.send(f"USER {self.client_config.email}\r\n".encode())
            response_user = mail_socket.recv(1024).decode()

            if response_user.startswith("+OK"):
                mail_socket.send(f"RETR {email_number}\r\n".encode())

                response_retr = ""
                while True:
                    data = mail_socket.recv(1024).decode()

                    if not data:
                        break

                    response_retr += data

                    if response_retr.endswith("\r\n.\r\n"):
                        break

                to_remove = data.split("\r\n")[0]
                response_retr = response_retr.removeprefix(to_remove + "\r\n")
                response_retr = response_retr.removesuffix("\r\n.\r\n")
                boundary = self.get_boundary(response_retr)

                # print("A")
                if boundary == None:  # khong co file
                    (
                        sender_name,
                        sender_email,
                        subject,
                        mail_content,
                    ) = self.extract_email_info(response_retr)
                    # print("B1")
                    # print(sender_name, sender_email, subject, mail_content)
                    self.load_email_to_managing(subject, sender_email, sender_name)
                else:  # co file
                    parts = self.split_message_by_boundary(response_retr, boundary)
                    # print("B2")
                    (
                        sender_name,
                        sender_email,
                        subject,
                    ) = self.extract_email_info_when_has_attachment(parts[0])
                    # print(parts[0])
                    # print("C")
                    # print(parts[1])
                    mail_content = self.get_text_content(parts[1])
                    # print("End C")
                    # print(mail_content)
                    self.load_email_to_managing(
                        subject, sender_email, sender_name, True
                    )
                    # print("D")
                    # with open("test.txt", "w") as file:
                    #    file.write(parts[2])

                    # print(subject)

                    for part in parts[2:]:
                        self.save_attachment(part, subject)
                    # print("E")

                """
                print('A')
                
                print('B')
                print()
                #print(boundary)
                #print(response_retr)
                print(len(parts))
                print('Phan 1')
                print(parts[0])
                print()
                print('Phan 2')
                print(parts[1])
                #print(parts[2])

                if "Content-Disposition: attachment" in response_retr: # có file
                    file_start = response_retr.rfind("Content-Type:")
                    attachment = response_retr[file_start:]
                    (
                        sender_name,
                        sender_email,
                        subject,
                        mail_content,
                    ) = self.extract_email_info_when_has_attachment(response_retr)

                    self.save_attachment(attachment, email_number, subject)
                    self.load_email_to_managing(
                        subject, sender_email, sender_name, True
                    )
                else: # không có file
                    (
                        sender_name,
                        sender_email,
                        subject,
                        mail_content,
                    ) = self.extract_email_info(response_retr)
                    #print(sender_name, sender_email, subject, mail_content)
                    self.load_email_to_managing(subject, sender_email, sender_name)
                """

                self.save_mail_content(subject, mail_content)

            else:
                print("Đăng nhập thất bại. Hãy kiểm tra lại.")
        except Exception as e:
            # print(f"Lỗi khi đọc mail: {e}")
            pass
        finally:
            mail_socket.close()

    def get_text_content(self, message):
        # Tìm vị trí của "Content-Type" trong chuỗi
        content_type_start = message.find("Content-Type:")

        # Kiểm tra xem "Content-Type" có tồn tại trong chuỗi không
        if content_type_start == -1:
            return None

        # Tìm vị trí của "\n" sau "Content-Type"
        content_type_end = message.find("\n", content_type_start)

        # Lấy giá trị "Content-Type"
        content_type_value = message[content_type_start:content_type_end].strip()
        # print("content type value:", content_type_value)

        # Kiểm tra xem có phải là văn bản không
        if "text/plain" not in content_type_value:
            return None

        # Tìm vị trí của "\n\n" để xác định nơi bắt đầu nội dung văn bản
        # print(content_type_end)
        content_start = message.find("\r\n", content_type_end)
        # print(content_start)
        # print(message[content_start])

        # Kiểm tra xem "\n\n" có tồn tại trong chuỗi không
        if content_start == -1:
            return None

        # Lấy nội dung văn bản
        text_content = message[content_start + 2 :].strip()
        # print("text content: ", text_content)

        return text_content

    def save_attachment(self, attachment, subject):
        def getFileName(attachment_header):
            index = attachment_header.find("name=") + 6
            file_name = attachment_header[index:]
            end_index = file_name.find("\r\n")
            file_name = file_name[: end_index - 1]

            return file_name

        attachment_end = attachment.find("\r\n\r\n")
        # attachment_header = attachment[:attachment_end]

        file_name = getFileName(attachment)
        # print(attachment_end)

        # print(file_name)

        attachment_data = attachment[attachment_end:]
        attachment_data = attachment_data.replace("\r\n", "")

        decode_data = base64.b64decode(attachment_data)

        attachment_directory = (
            "./Mailbox/" + self.client_config.email + "/Inbox/" + subject + "/"
        )
        if not os.path.exists(attachment_directory):
            os.makedirs(attachment_directory)

        attachment_file_path = attachment_directory + file_name

        with open(attachment_file_path, "wb") as file:
            file.write(decode_data)

        # print(f"Đã lưu file đính kèm của Email {email_number} vào đường dẫn: {attachment_file_path}")

    def extract_email_info(self, email_content):
        msg = email.message_from_string(email_content)
        sender = msg.get("From")

        subject = decode_header(msg.get("Subject"))[0][0]

        if isinstance(subject, bytes):
            subject = subject.decode()

        sender_email = sender[sender.find("<") + 1 : sender.find(">")]
        sender_name = sender[: sender.find(sender_email) - 2]

        if msg.is_multipart():
            main_content = msg.get_payload()[0].get_payload()
        else:
            main_content = msg.get_payload()

        return sender_name, sender_email, subject, main_content

    def extract_email_info_when_has_attachment(self, email_content):
        sender_name = email_content[email_content.find("From: ") + len("From: ") :]

        sender_email = sender_name[
            sender_name.find("<") + 1 : sender_name.find(">")
        ].strip()  # final
        subject = sender_name[sender_name.find("Subject: ") + len("Subject: ") :]
        subject = subject[: subject.find("\n")].strip()  # final

        """
        main_content = sender_name[sender_name.find("Content-Transfer-Encoding:") :]
        main_content = main_content[main_content.find("\n") :]
        main_content = main_content[: main_content.find("-") - 1].strip()
        main_content = main_content.replace("\n", "")  # final
        """

        sender_name = sender_name[: sender_name.find(" <")].strip()  # final

        return sender_name, sender_email, subject

    def mark_email_as_read(self, email_number):
        self.read_emails.add(email_number)
        self.save_state(self.read_emails)
        print(f"Email {email_number} marked as read.")

    def print_list(self):
        print("DEBUG: Emails structure:", self.read_emails)
        print("Đây là danh sách email trong mailbox của bạn: ")
        if not self.read_emails:
            print("Trống")
        else:
            number = 1
            for email in self.read_emails:
                print("DEBUG: Current email tuple:", email)
                is_read = ""
                if not email[3]:
                    is_read = "(chưa đọc)"
                print(f"{number}.{is_read} {email[0]} {email[1]}")
                number += 1


def call_getting_email(buffer_config):
    # Replace these values with your actual configurations
    email_config = ClientConfig(
        mailserver=buffer_config["MailServer"],
        pop3=buffer_config["POP3"],
        email=buffer_config["Email"],
        filters=[
            EmailFilter("Folder1", ["flag1", "flag2"]),
            EmailFilter("Folder2", ["flag3"]),
        ],
    )

    # Example usage of EmailDownloader
    downloader = EmailDownloader(email_config)
    listDownloaded = downloader.download_emails()

    # print(listDownloaded)

    # Example usage of EmailReader
    reader = EmailReader(email_config)

    for email_number in listDownloaded:
        reader.read_email(email_number)
