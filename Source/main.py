import sys

sys.dont_write_bytecode = True

import sending_email
import getting_email
import console
import setting
import threading

exit_flag = False


def print_menu(buffer_config):
    while True:
        choice = console.print_client_console()

        if choice == 4:
            global exit_flag
            exit_flag = True
            break

        if choice == 1:  # Using for sending Email
            buffer_sending = console.printSendingEmail()
            sending_email.call_sending_email(buffer_config, buffer_sending)

        elif choice == 2:
            console.print_received_email_list(buffer_config["Email"])

        elif choice == 3:
            setting.setting()
        else:
            pass


def get_email_loop(buffer_config):
    if not exit_flag:
        buffer_config = setting.read_config()
        getting_email.call_getting_email(buffer_config)
        threading.Timer(
            buffer_config["Autoload"], get_email_loop, args=[buffer_config]
        ).start()


# Print Mail Client on Console
def main():
    setting.create_or_check_config_file()

    buffer_config = setting.read_config()

    thread = threading.Thread(target=get_email_loop, args=(buffer_config,))
    thread.start()

    print_menu(buffer_config)
    thread.join()


if __name__ == "__main__":
    main()
