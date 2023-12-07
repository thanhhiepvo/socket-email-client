import os
import socket
import logging
import json

class ClientConfig:
    def __init__(self, email, mailserver, pop3, filters):
        self.email = email
        self.mailserver = mailserver
        self.pop3 = pop3
        self.filters = filters

logging.basicConfig(level=logging.ERROR)

class EmailFilter:
    def __init__(self, folder, flags):
        self.folder = folder
        self.flags = flags

class EmailDownloader:
    def __init__(self, client_config):
        self.client_config = client_config
        self.state_filename = "download_state.txt"
        self.downloaded_emails = self.load_state()

    def save_state(self, state):
        with open(self.state_filename, "w") as state_file:
            state_file.write(",".join(map(str, state)))

    def load_state(self):
        if os.path.exists(self.state_filename):
            with open(self.state_filename, "r") as state_file:
                state_content = state_file.read().strip()

                if state_content:
                    return set(map(int, state_content.split(',')))
                else:
                    return set()
        else:
            return set()

    def should_save_to_folder(self, email_content, flags):
        for flag in flags:
            if flag in email_content:
                return True
        return False
    
    def appendUnread(self, msg_num, mailbox_path):
        file_json = mailbox_path + "/unread.json"
        file_name = str(msg_num) + ".msg"

        data = []
        if os.path.exists(file_json):
            f = open(file_json)
            data = json.load(f)
            f.close()
            data = data['unread']
        data.append(file_name)

        json_data = {
            "unread": data
        }

        with open(file_json, 'w') as file:
            json.dump(json_data, file, indent=4)

    def save_mail(self, msg_num, email_content):
        email_content = email_content.replace("\r\n", "\n")
        mailbox_path = "./Mailbox/" + self.client_config.email
        if not os.path.exists(mailbox_path):
            os.makedirs(mailbox_path)

        saved = False

        # Phân loại email và tải về các folder cụ thể
        for filter in self.client_config.filters:
            if self.should_save_to_folder(email_content, filter.flags):
                filter_folder = os.path.join(mailbox_path, filter.folder)
                if not os.path.exists(filter_folder):
                    os.makedirs(filter_folder)

                filename = f"{filter_folder}/{msg_num}.msg"
                with open(filename, "w") as file:
                    file.write(email_content)
                
                saved = True
        emails = []

        if not saved:
            filter_folder = os.path.join(mailbox_path, './Inbox')
            if not os.path.exists(filter_folder):
                os.makedirs(filter_folder)
            filename = f"{filter_folder}/{msg_num}.msg"
            with open(filename, "w") as file:
                file.write(email_content)

        self.appendUnread(msg_num, mailbox_path)
            
    def download_emails(self):
        try:
            # Mở socket
            mail_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.client_config.mailserver, self.client_config.pop3)
            mail_socket.connect(server_address)

            # Nhận câu trả lời đầu tiên
            response_user = mail_socket.recv(1024).decode()

            # Gửi lệnh USER
            mail_socket.send(f"USER {self.client_config.email}\r\n".encode())
            response_user = mail_socket.recv(1024).decode()

            # Gửi lệnh LIST
            mail_socket.send(f"LIST\r\n".encode())
            response_list = mail_socket.recv(1024).decode()
            # print(f"List: {response_list}")

            # Lấy danh sách các email
            messages = response_list.split("\r\n")[1:-2]

            # Lưu từng email
            for message in messages:
                msg_num = int(message.split()[0])
                
                # Kiểm tra lại trạng thái tải của email
                # Nếu email chưa được tải thì bắt đầu tải về
                if msg_num not in self.downloaded_emails:
                    mail_socket.send(f"RETR {msg_num}\r\n".encode())

                    email_content = ""
                    while True:
                        data = mail_socket.recv(1024).decode()

                        if not data:
                            break
                    
                        email_content += data

                        if email_content.endswith('\r\n.\r\n'):
                            break

                    # Loại bỏ dòng đầu tiên "+OK ..."
                    to_remove = email_content.split("\r\n")[0] 
                    email_content = data.removeprefix(to_remove + "\r\n")
                    
                    # loại bỏ dòng cuối cùng
                    email_content = email_content.removesuffix('\r\n.\r\n')
                    
                    self.save_mail(msg_num, email_content)
                    
                    self.downloaded_emails.add(msg_num)
                    self.save_state(self.downloaded_emails)

        except socket.error as se:
            logging.error(f"Socket Error: {se}")
        except IOError as ioe:
            logging.error(f"I/O Error: {ioe}")
        except Exception as e:
            logging.error(f"Error: {e}")
             