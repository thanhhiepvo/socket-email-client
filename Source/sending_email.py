import base64
import socket
import os
from datetime import datetime
import uuid


CRLF = "\r\n"
buff_size = 1024
boundary = "boundary"


class Error(Exception):
    pass


def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def detect_error(client_socket, response_code, error_message):
    received_data = client_socket.recv(1024).decode()
    if received_data[:3] != str(response_code):
        raise Error(error_message)


def connect_server(client_socket, server_id, port):
    client_socket.connect((server_id, port))
    detect_error(client_socket, 220, "Lỗi kết nối server!!")


def send_line(client_socket, message=None):
    client_socket.send((message + CRLF).encode())


def send_command(client_socket, command, response_code):
    send_line(client_socket, command)
    detect_error(client_socket, response_code, f"Lỗi ở lệnh {command}!!")


def greet_server(client_socket):
    send_command(client_socket, "EHLO server.com", 250)


def begin_sending_mail(client_socket, sender_email, receiver_emails):
    send_command(client_socket, f"MAIL FROM: <{sender_email}>", 250)
    for receiver_email in receiver_emails:
        send_command(client_socket, f"RCPT TO: <{receiver_email}>", 250)
    send_command(client_socket, "DATA", 354)


def end_sending_mail(client_socket, boundary=None):
    if boundary:
        send_line(client_socket, "--" + boundary + "--")
    send_command(client_socket, ".", 250)


def close_connection(client_socket):
    send_command(client_socket, "QUIT", 221)
    client_socket.close()


def generate_message_id():
    message_id = f"<{uuid.uuid4()}@gmail.com>"
    return message_id


def get_current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%a, %d %b %Y %H:%M:%S +0700")
    return formatted_time


def generate_email_sequence(emails):
    emails_sequence = emails[0]
    for i in range(1, len(emails)):
        emails_sequence += ", " + emails[i]
    return emails_sequence


def get_file_name(file_path):
    return os.path.basename(file_path)


def get_content_type(file_path):
    file_extension = os.path.splitext(file_path)[1][1:].lower()
    if file_extension == "txt":
        return "text/plain"
    elif file_extension == "pdf" or file_extension == "zip":
        return "application/" + file_extension
    elif file_extension == "rar":
        return "application/x-rar-compressed"
    elif file_extension == "doc":
        return "application/msword"
    elif file_extension == "docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif file_extension == "ppt":
        return "application/vnd.ms-powerpoint"
    elif file_extension == "pptx":
        return (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    elif file_extension == "xls":
        return "application/vnd.ms-excel"
    elif file_extension == "xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_extension == "jpg" or file_extension == "jpeg":
        return "image/jpeg"
    elif file_extension == "gif" or file_extension == "png":
        return "image" + file_extension
    elif file_extension == "mp3":
        return "audio/mpeg"
    elif file_extension == "wav":
        return "audio/wav"
    elif file_extension == "mp4":
        return "video/mp4"
    else:
        return "application/octet-stream"


def generate_mime_part_header(boundary, file_path=None):
    mime_part_header = "--" + boundary + CRLF
    mime_part_header += "Content-Type: "
    if file_path:
        mime_part_header += get_content_type(file_path)
        file_name = get_file_name(file_path)
        mime_part_header += f'; name="{file_name}"' + CRLF
        mime_part_header += (
            f'Content-Disposition: attachment; filename="{file_name}"' + CRLF
        )
        mime_part_header += "Content-Transfer-Encoding: base64" + CRLF
    else:
        mime_part_header += "text/plain; "
        mime_part_header += "charset=UTF-8; format=flowed" + CRLF
        mime_part_header += "Content-Transfer-Encoding: quoted-printable" + CRLF
    return mime_part_header


def generate_general_header(
    sender_name, sender_email, to_emails, cc_emails, subject, attached=False
):
    general_header = ""
    if attached:
        general_header += f"Content-Type: multipart/mixed; boundary={boundary}"
        general_header += CRLF
    general_header += f"Message-ID: {generate_message_id()}" + CRLF
    general_header += f"Date: {get_current_time()}" + CRLF
    general_header += "MIME-Version: 1.0" + CRLF
    general_header += "Content-Language: en-US" + CRLF
    general_header += f"From: {sender_name} <{sender_email}>" + CRLF
    general_header += f"To: {generate_email_sequence(to_emails)}" + CRLF
    if len(cc_emails) > 0:
        general_header += f"Cc: {generate_email_sequence(cc_emails)}" + CRLF
    general_header += f"Subject: {subject}" + CRLF
    return general_header


def check_file_size(file_path):
    return os.path.getsize(file_path) <= 3 * 1024 * 1024


def get_file_data(file_path):
    if not os.path.exists(file_path):
        raise Error("File được đính kèm không tồn tại!!")
    with open(file_path, "rb") as file:
        data = base64.b64encode(file.read()).decode()
    block = ""
    line_limit = 72
    for i in range(0, len(data), line_limit):
        block += data[i : i + line_limit] + CRLF
    return block


def send_email(
    client_socket,
    sender_name,
    sender_email,
    to_emails,
    cc_emails,
    bcc_emails,
    subject,
    message,
    attachment_paths=None,
):
    receiver_emails = to_emails + cc_emails + bcc_emails
    begin_sending_mail(client_socket, sender_email, receiver_emails)
    if attachment_paths:
        general_header = generate_general_header(
            sender_name, sender_email, to_emails, cc_emails, subject, True
        )
        send_line(client_socket, general_header)
        send_line(client_socket, generate_mime_part_header(boundary))
        send_line(client_socket, message + CRLF)
        for file_path in attachment_paths:
            if check_file_size(file_path):
                send_line(client_socket, generate_mime_part_header(boundary, file_path))
                send_line(client_socket, get_file_data(file_path))
            else:
                print(
                    f"{get_file_name(file_path)} có dung lượng lớn hơn 3MB nên sẽ không được gửi đi!!"
                )
        end_sending_mail(client_socket, boundary)
    else:
        send_line(
            client_socket,
            generate_general_header(
                sender_name, sender_email, to_emails, cc_emails, subject
            ),
        )
        send_line(client_socket, message)
        end_sending_mail(client_socket)


def call_sending_email(buffer_config, buffer_sending):
    client_socket = create_socket()
    connect_server(client_socket, buffer_config["MailServer"], buffer_config["SMTP"])
    send_email(
        client_socket,
        buffer_config["Username"],
        buffer_config["Email"],
        buffer_sending["To"],
        buffer_sending["CC"],
        buffer_sending["BCC"],
        buffer_sending["subject"],
        buffer_sending["content"],
        buffer_sending["filePaths"],
    )
