import os
import socket
import logging

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
        self.state_folder = "State"
        self.state_filename = f"{self.client_config.email}.txt"
        self.state_filepath = os.path.join(self.state_folder, self.state_filename)
        self.downloaded_emails = self.load_state()
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

    def save_mail(self, msg_num, email_content):
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
            
    def download_emails(self):
        try:
            mail_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.client_config.mailserver, self.client_config.pop3)
            mail_socket.connect(server_address)
            response_user = mail_socket.recv(1024).decode()
            mail_socket.send(f"USER {self.client_config.email}\r\n".encode())
            response_user = mail_socket.recv(1024).decode()
            mail_socket.send(f"LIST\r\n".encode())
            response_list = mail_socket.recv(1024).decode()
            messages = response_list.split("\r\n")[1:-2]

            listDownloaded  = []
            for message in messages:
                msg_num = int(message.split()[0])
                if msg_num not in self.downloaded_emails:
                    listDownloaded.append(msg_num)
                    
                    self.downloaded_emails.add(msg_num)
                    self.save_state(self.downloaded_emails)

            return listDownloaded

        except socket.error as se:
            logging.error(f"Socket Error: {se}")
        except IOError as ioe:
            logging.error(f"I/O Error: {ioe}")
        except Exception as e:
            logging.error(f"Error: {e}")
             
