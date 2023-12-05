import json
import os

def create_or_check_config_file(file_path='config.json'):
    if os.path.exists(file_path):
        return
    
    default_data = {
        "General": [
            {
                "Username": "Test Name",
                "Email": "test@email.com",
                "Password": "ahihi",
                "MailServer": "127.0.0.1",
                "SMTP": 2225,
                "POP3": 3335,
                "Autoload": 10
            }
        ]
    }

    with open(file_path, 'w') as file:
        json.dump(default_data, file, indent=4)

def readConfig():
    f = open('config.json')
    data = json.load(f)
    f.close()

    return data['General'][0]

def setting():
    file_json = 'config.json'

    f = open(file_json)
    data = json.load(f)
    f.close()

    data = data['General'][0]

    while True:
        print("Thông tin và Cài đặt")
        print("1. Username:", data['Username'])
        print("2. Email:", data['Email'])
        print("3. Password:", data['Password'])
        print("4. MailServer:", data['MailServer'])
        print("5. SMTP:", data['SMTP'])
        print("6. POP3:", data['POP3'])
        print("7. Autoload:", data['Autoload'])
        print("8. EXIT")

        choice = int(input("Chọn mục để sửa (nhập số): "))
        while choice not in range(1, 9):
            choice = int(input("Nhập lại: "))

        if choice == 1:
            data['Username'] = str(input("Nhập username: "))
        elif choice == 2:
            data['Email'] = str(input("Nhập email: "))
        elif choice == 3:
            data['Password'] = str(input("Nhập password: "))
        elif choice == 4:
            data['MailServer'] = str(input("Nhập MailServer host: "))
        elif choice == 5:
            data['SMTP'] = int(input("Nhập SMTP: "))
        elif choice == 6:
            data['POP3'] = int(input("Nhập POP3: "))
        elif choice == 7:
            data['Autoload'] = int(input("Nhập Autoload: "))
        else:
            break

        if choice != 8:
            print()

    json_data = {
        'General': [
            data
        ]
    }

    with open(file_json, 'w') as file:
        json.dump(json_data, file, indent=4)