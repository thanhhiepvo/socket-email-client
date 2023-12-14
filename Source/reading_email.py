import json
import os
import shutil
import glob


def read_manage_json(email):
    file_path = "./Mailbox/" + email + "/manage.json"

    with open(file_path, "r") as file:
        manage_data = json.load(file)

    data = manage_data["emails"]

    return data


def write_manage_json(email, data):
    file_path = "./Mailbox/" + email + "/manage.json"
    json_data = {"emails": data}

    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)


def get_mail_in_box(data, box):
    box_data = []
    for i in range(len(data)):
        if data[i]["box"] == box:
            box_data.append(data[i])

    return box_data


def print_mails_into_console(data):
    count = 1
    for item in data:
        if item["read"] == "No":
            print(
                "(chưa đọc)",
                count,
                ". Sender:",
                item["sender_name"],
                ", Subject:",
                item["subject"],
            )
        else:
            print(
                "         ",
                count,
                ". Sender:",
                item["sender_name"],
                ", Subject:",
                item["subject"],
            )
        count += 1


def get_mail_content(data, choice_file, email, choice_Mailbox):
    mail = data[choice_file]

    mail_directory = (
        "./Mailbox/" + email + "/" + choice_Mailbox + "/" + mail["subject"] + ".msg"
    )

    with open(mail_directory, "r") as file:
        content = file.read()

    return content


def mark_file_was_read_on_disk(email, mail_card):
    file_path = "./Mailbox/" + email + "/manage.json"

    with open(file_path, "r") as file:
        config_data = json.load(file)

    data = config_data["emails"]
    for i in range(len(data)):
        if data[i] == mail_card:
            data[i]["read"] = "Yes"

    json_data = {"emails": data}
    with open(file_path, "w") as file:
        json.dump(json_data, file, indent=4)


def get_file_name_in_folder(folder_path):
    files = glob.glob(os.path.join(folder_path, "*"))
    files = [f for f in files if os.path.isfile(f)]
    file = files[0]
    file = file[file.rfind("\\") + 1 :]
    return file


def move_file(email, the_email, des_box):
    data = read_manage_json(email)
    index = data.index(the_email)

    source_folder = "./Mailbox/" + email + "/" + the_email["box"] + "/"
    des_folder = "./Mailbox/" + email + "/" + des_box + "/"

    if not os.path.exists(des_folder):
        os.makedirs(des_folder)

    file_name = the_email["subject"] + ".msg"

    src_path = os.path.join(source_folder, file_name)
    des_path = os.path.join(des_folder, file_name)

    print("src path:", src_path)
    print("des path:", des_path)

    try:
        shutil.move(src_path, des_path)
    except Exception as e:
        print(f"An error occurred: {e}")

    if the_email["attachment"] == True:
        source_folder += the_email["subject"] + "/"
        des_folder += "/" + the_email["subject"] + "/"

        if not os.path.exists(des_box):
            os.makedirs(des_folder)

        file_name = get_file_name_in_folder(source_folder)

        src_path = os.path.join(source_folder, file_name)
        des_path = os.path.join(des_folder, file_name)

        try:
            shutil.move(src_path, des_path)
        except Exception as e:
            print(f"An error occurred: {e}")

        # os.rmdir(src_path)
        os.rmdir(source_folder)

    data[index]["box"] = des_box
    write_manage_json(email, data)
