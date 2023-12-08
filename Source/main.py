import sys
sys.dont_write_bytecode = True

import sending_email
import getting_email
import console
import setting

# Print Mail Client on Console
def main():
    setting.create_or_check_config_file()
    buffer_config = setting.readConfig()
    #print(buffer_config)

    getting_email.call_getting_email(buffer_config)

    choice = console.printClientConsole()

    if choice == 1: # Using for sending Email
        buffer_sending = console.printSendingEmail()
        print(buffer_sending)
        sending_email.call_sending_email(buffer_config, buffer_sending)

    elif choice == 2:
        console.printReceivedEmailList(buffer_config['Email'])

    elif choice == 3:
        setting.setting()
    else:
        pass

if __name__ == "__main__":
    main()
