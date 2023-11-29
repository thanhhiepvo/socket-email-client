# Viewing Email
import email
from email import policy
from email.parser import BytesParser
from email.header import decode_header

import socket
import mimetypes
import os
import re

# Biến toàn cục để lưu trạng thái
downloaded_emails = set()
emails = []

# Tạo socket
def create_mail_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Kết nối đến server
def connect_to_server(mail_socket, pop_server, port):
    try:
        mail_socket.connect((pop_server, port))
        response = mail_socket.recv(1024).decode()
        
        if response.startswith('+OK'):
            print(f"Setsuzoku ni seiko shi mashi ta. Server {pop_server}:{port}")
        else:
            print(f"Kết nối thất bại. Server không phản hồi {response}")

    except Exception as e:
        print(f"Không thể kết nối đến server {e}")

# Ngắt kết nối server
def close_connection(mail_socket):
    try:
        mail_socket.send("QUIT\r\n".encode())
        response_quit = mail_socket.recv(1024).decode()

    except Exception as e:
        print(f"Không thể ngắt kết nối server. {e}")
    else:
        print("Server ga setsudan sa re mashi ta .Go aisatsu 、 mata o ai shi masho u . <3")
        
    finally:
        mail_socket.close()

# Lưu State
def save_state(state):
    with open("email_state.txt", "w") as state_file:
        state_file.write(",".join(map(str, state)))

# Tải State
def load_state():
    if os.path.exists("email_state.txt"):
        with open("email_state.txt", "r") as state_file:
            state_content = state_file.read().strip()

            if state_content:
                return set(map(int, state_content.split(',')))
            else:
                return set()
    else:
        return set()

# Tải nội dung email
def download_emails(mail_socket, username):
    global downloaded_mails
    global mails
    mail_socket.send(f"USER {username}\r\n".encode())
    response_user = mail_socket.recv(1024).decode()

    downloaded_emails = load_state()

    mail_socket.send("LIST\r\n".encode())
    response_list = mail_socket.recv(1024).decode()
    print(f"List: {response_list}")

    messages = response_list.split("\r\n")[1:-2]

    for message in messages:
        msg_num = int(message.split()[0])

        if msg_num not in downloaded_emails:
            mail_socket.send(f"RETR {msg_num}\r\n".encode())

            # Start with an empty string to store the email content
            email_content = ""

            # Loop until the end of the email content is reached
            while True:
                data = mail_socket.recv(1024).decode()
                if not data:
                    break
                email_content += data

                # Check for the end of the email content
                if email_content.endswith('\r\n.\r\n'):
                    break

            # Đánh dấu là đã tải
            downloaded_emails.add(msg_num) 

            # Thêm thông tin vào danh sách emails
            # sender, subject, main_content = extract_email_info(email_content)
            # is_read = False
            # emails.append((sender, subject, main_content, is_read))

    # Lưu trạng thái sau khi tải xong
    save_state(downloaded_emails)
    
# Hàm đọc email
def read_email(mail_socket, username, email_number):
    # Thực hiện lệnh USER
    mail_socket.send(f"USER {username}\r\n".encode())
    response_user = mail_socket.recv(1024).decode()

    # Kiểm tra trạng thái lệnh PASS
    if response_user.startswith('+OK'):
        # Nếu đăng nhập thành công, thực hiện lệnh RETR để lấy nội dung của email
        mail_socket.send(f"RETR {email_number}\r\n".encode())
        
        # Loop to receive the entire email content
        response_retr = ""
        while True:
            data = mail_socket.recv(1024).decode()
            if not data:
                break
            response_retr += data
            
            # Kiểm tra xem tới cuối nội dung email chưa
            if response_retr.endswith('\r\n.\r\n'):
                break

        # print(f"After RETR {email_number} command: {response_retr}")
        # In ra nội dung của email
        print(f"Nội dung email:\n{response_retr}")
        
        # Đánh dấu email đã đọc
        # emails[email_number - 1] = (emails[email_number - 1][0], emails[email_number - 1][1], emails[email_number - 1][2], True)

        # Kiểm tra xem email có file đính kèm không
        if "Content-Disposition: attachment" in response_retr:
            attachment_start = response_retr.find("Content-Disposition: attachment")
            save_attachment(response_retr, attachment_start, email_number)
    else:
        print("Đăng nhập thất bại. Hãy kiểm tra lại.")

def get_boundary(email_content, attachment_start):
    # Find the boundary parameter in the Content-Type header
    content_type_index = email_content.find("Content-Type", attachment_start)
    boundary_start_index = email_content.find("boundary=", content_type_index)
    boundary_end_index = email_content.find("\r\n", boundary_start_index)
    
    # Extract the boundary string
    boundary = email_content[boundary_start_index + len("boundary="):boundary_end_index].strip()
    
    # Clean up the boundary string
    boundary = boundary.replace('"', "")
    
    return boundary

# Hàm để đọc và lưu file đính kèm
def save_attachment(email_content, attachment_start, email_number):
    # Tìm vị trí kết thúc của dữ liệu đính kèm
    attachment_end = email_content.find("\r\n\r\n", attachment_start)
    attachment_data = email_content[attachment_end:].encode()

    # Lấy đối tượng email từ nội dung email
    email_message = BytesParser(policy=policy.default).parsebytes(email_content.encode())

    # Xác định loại nội dung của file đính kèm
    content_type = email_message.get_content_type()
    
    # Lấy mô tả nếu có
    content_disposition, params = email_message.get_content_disposition(), email_message.get_params()

    # Giải mã tên file nếu có
    if params:
        filename_info = decode_header(params.get('filename', ''))
        filename = filename_info[0][0] if filename_info[0][0] else "unknown_attachment"
    else:
        filename = "unknown_attachment"

    # Thư mục để lưu tệp đính kèm
    attachment_directory = "C:/Users/htdat/Desktop/Source/VS_code/Python/Socket Project/Attachments"

    # Kiểm tra xem thư mục tồn tại chưa, nếu chưa thì tạo mới
    if not os.path.exists(attachment_directory):
        os.makedirs(attachment_directory)

    # Xác định đường dẫn lưu file đính kèm
    attachment_file_path = os.path.join(attachment_directory, f"attachment_{email_number}_{filename}")

    # Lưu dữ liệu file đính kèm xuAống máy cục bộ của client
    with open(attachment_file_path, "wb") as attachment_file:
        attachment_file.write(attachment_data)

    print(f"Đã lưu file đính kèm của Email {email_number} vào đường dẫn: {attachment_file_path}")



def extract_email_info(email_content):
    # Phân tích nội dung email
    msg = email.message_from_string(email_content)

    # Trích xuất người gửi
    sender = msg.get('From')

    # Trích xuất chủ đề
    subject = decode_header(msg.get('Subject'))[0][0]
    if isinstance(subject, bytes):
        # Nếu chủ đề là bytes, hãy chuyển đổi nó thành chuỗi
        subject = subject.decode()

    # Trích xuất nội dung chính
    if msg.is_multipart():
        # Nếu email có nhiều phần, hãy lấy phần đầu tiên
        main_content = msg.get_payload()[0].get_payload()
    else:
        # Nếu không, chỉ cần lấy nội dung
        main_content = msg.get_payload()

    return sender, subject, main_content

def print_list(emails):
    print("Đây là danh sách email trong mailbox của bạn: ")
    
    if not emails:
        print("Trống")
    else:
        number = 1
        for email in emails: 
            is_read = ''
            
            if not email[3]:
                is_read = "(chưa đọc)"
                
            print(f"{number}.{is_read} {email[0]} {email[1]}")
            number += 1

if __name__ == "__main__":
    # Tạo mail socket
    mail_socket = create_mail_socket()
    # Thông tin
    pop_server = "127.0.0.1"
    port = 3335
    
    username = "htdat222@clc.fitus.edu.vn"
    # Kết nối đến server
    connect_to_server(mail_socket, pop_server, port)
    
    # Tiến hành tải email
    if mail_socket:
        download_emails(mail_socket, username)     
    
    # print_list(emails)
    
    email_number = int(input("Dono meru wa yomi tai desu ka: "))
    read_email(mail_socket, username, email_number)
    
    # Ngắt kết nối server
    close_connection(mail_socket)