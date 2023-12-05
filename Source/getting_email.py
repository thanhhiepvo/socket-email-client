import os
import email
from email.parser import BytesParser
from email import policy
from email.header import decode_header
import socket

from download_email import ClientConfig 
from download_email import EmailFilter
from download_email import EmailDownloader

class EmailReader:
    def __init__(self, client_config):
        self.client_config = client_config
        self.state_filename = "read_state.txt"
        self.read_emails = self.load_state()

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
        
    def read_email(self, email_number):
        try:
            # Mở socket
            mail_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.client_config.mailserver, self.client_config.pop3)
            mail_socket.connect(server_address)
            
            # Nhận câu trả lời đầu tiên
            response = mail_socket.recv(1024).decode()

            # Gửi lệnh USER
            mail_socket.send(f"USER {self.client_config.email}\r\n".encode())
            response_user = mail_socket.recv(1024).decode()
            # print(response_user)

            # Nếu server trả lời "+OK"
            if response_user.startswith('+OK'):
                # Gửi lệnh RETR để lấy email cụ thể
                mail_socket.send(f"RETR {email_number}\r\n".encode())

                response_retr = ""
                while True:
                    data = mail_socket.recv(1024).decode()

                    if not data:
                        break

                    response_retr += data

                    if response_retr.endswith('\r\n.\r\n'):
                        break

                # Loại bỏ dòng đầu tiên
                to_remove = data.split("\r\n")[0] 
                response_retr = response_retr.removeprefix(to_remove + "\r\n")

                # loại bỏ dòng cuối cùng
                response_retr = response_retr.removesuffix('\r\n.\r\n')
                
                # Xuất ra màn hình nội dung mail vừa lấy
                print(f"Nội dung email:\n{response_retr}")

                # Lưu file đính kèm nếu có
                if "Content-Disposition: attachment" in response_retr:
                    attachment_start = response_retr.find("Content-Disposition: attachment")
                    self.save_attachment(response_retr, attachment_start, email_number)
            else:
                print("Đăng nhập thất bại. Hãy kiểm tra lại.")
        except Exception as e:
            print(f"Error while reading email: {e}")
        finally:
            # Đóng socket sau khi hoàn thành
            mail_socket.close()

    def save_attachment(self, email_content, attachment_start, email_number):
        attachment_end = email_content.find("\r\n\r\n", attachment_start)
        attachment_data = email_content[attachment_end:].encode()

        email_message = BytesParser(policy=policy.default).parsebytes(email_content.encode())
        content_type = email_message.get_content_type()

        content_disposition, params = email_message.get_content_disposition(), email_message.get_params()

        if params:
            filename_info = decode_header(params.get('filename', ''))
            filename = filename_info[0][0] if filename_info[0][0] else "unknown_attachment"
        else:
            filename = "unknown_attachment"

        attachment_directory = os.path.join(".", "Attachments", self.client_config.email)

        if not os.path.exists(attachment_directory):
            os.makedirs(attachment_directory)

        attachment_file_path = os.path.join(attachment_directory, f"attachment_{email_number}_{filename}")

        with open(attachment_file_path, "wb") as attachment_file:
            attachment_file.write(attachment_data)

        print(f"Đã lưu file đính kèm của Email {email_number} vào đường dẫn: {attachment_file_path}")

    def extract_email_info(self, email_content):
        msg = email.message_from_string(email_content)
        sender = msg.get('From')
        subject = decode_header(msg.get('Subject'))[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        if msg.is_multipart():
            main_content = msg.get_payload()[0].get_payload()
        else:
            main_content = msg.get_payload()

        return sender, subject, main_content

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

                is_read = ''
                if not email[3]:
                    is_read = "(chưa đọc)"

                print(f"{number}.{is_read} {email[0]} {email[1]}")
                number += 1

def call_getting_email(buffer_config):
    # Replace these values with your actual configurations
    email_config = ClientConfig(
        mailserver = buffer_config['host'],
        pop3 = buffer_config['POP3'],
        email = buffer_config['email'],
        filters = [EmailFilter("Folder1", ["flag1", "flag2"]), EmailFilter("Folder2", ["flag3"])]
    )

    # Example usage of EmailDownloader
    downloader = EmailDownloader(email_config)
    downloader.download_emails()

    # Example usage of EmailReader
    reader = EmailReader(email_config)
    reader.print_list()

    email_number = int(input("Enter the email number you want to read: "))
    reader.read_email(email_number)

"""
def main():
    # Replace these values with your actual configurations
    email_config = ClientConfig(
        mailserver="127.0.0.1",
        pop3=3335,
        email="htdat222@clc.fitus.edu.vn",
        filters=[EmailFilter("Folder1", ["flag1", "flag2"]), EmailFilter("Folder2", ["flag3"])]
    )

    # Example usage of EmailDownloader
    downloader = EmailDownloader(email_config)
    downloader.download_emails()

    # Example usage of EmailReader
    reader = EmailReader(email_config)
    reader.print_list()

    email_number = int(input("Enter the email number you want to read: "))
    reader.read_email(email_number)

if __name__ == "__main__":
    main()
"""