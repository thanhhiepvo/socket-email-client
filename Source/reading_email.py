import json

def read_manage_json(email):
    file_path = "./Mailbox/" + email + "/manage.json"

    with open(file_path, 'r') as file:
        config_data = json.load(file)

    data = config_data['emails']
    
    return data

def get_mail_in_box(data, box):
    box_data = []
    for i in range(len(data)):
        if data[i]['box'] == box:
            box_data.append(data[i])
    
    return box_data

def print_mails_into_console(data):
    count = 1
    for item in data:
        if item['read'] == 'No':
            print(count, ". Sender:", item["sender_name"], ", Subject:", item["subject"], " (chưa đọc)")
        else:
            print(count, ". Sender:", item["sender_name"], ", Subject:", item["subject"])
        count += 1

def print_mail_content(data, choice_file, email, nMailbox):
    choice_file -= 1
    mail = data[choice_file]

    mail_directory = './Mailbox/' + email + '/' + nMailbox + '/' + mail['subject'] + '.msg'
    
    with open(mail_directory, "r") as file:
        content = file.read()

    return content

def markFileWasRead(email, subject):
    file_path = "./Mailbox/" + email + "/manage.json"

    with open(file_path, 'r') as file:
        config_data = json.load(file)

    data = config_data['emails']
    for i in range(len(data)):
        if data[i]['subject'] == subject:
            data[i]['read'] = "Yes"

    json_data = {
        "emails": data
    }
    
    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)