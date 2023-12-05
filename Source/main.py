import sending_email
import getting_email
import console

def readFileConfig():
    fileConfig = "config.txt"

    username, email, password, host, SMTP, POP3, Autoload = "", "", "", "", "", "", ""
    with open(fileConfig, "r") as file:
        lines = file.read()
        lines = lines.split('\n') # convert to list
        
        username = lines[1].split(': ')[1].split('<')[0].strip()
        email = lines[1].split('<')[1].split('>')[0]
        password = lines[2].split(': ')[1]
        host = lines[3].split(': ')[1]
        SMTP = lines[4].split(': ')[1]
        POP3 = lines[5].split(': ')[1]
        Autoload = lines[6].split(': ')[1]

        file.close()
    
    buffer = dict()
    buffer['username'] = username
    buffer['email'] = email
    buffer['password'] = password
    buffer['host'] = host
    buffer['SMTP'] = int(SMTP)
    buffer['POP3'] = int(POP3)
    buffer['Autoload'] = int(Autoload)

    #return username, email, password, host, int(SMTP), int(POP3), int(Autoload)
    return buffer

# Print Mail Client on Console
def main():
    #username, email, password, host, SMTP, POP3, Autoload = readFileConfig()
    buffer_config = readFileConfig()
    print(buffer_config)

    getting_email.call_getting_email(buffer_config)

    choice = console.printClientConsole()

    if choice == 1: # Using for sending Email
        buffer_sending = console.printSendingEmail()
        print(buffer_sending)
        sending_email.call_sending_email(buffer_config, buffer_sending)

    elif choice == 2:
        console.printReceivedEmailList()
    else:
        pass

if __name__ == "__main__":
    main()
