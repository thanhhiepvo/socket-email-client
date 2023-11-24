#import sending_email
import viewing_email

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

    return username, email, password, host, SMTP, POP3, Autoload

# Print Mail Client on Console
def main():
    username, email, password, host, SMTP, POP3, Autoload = readFileConfig()
    #print(username, email, password, host, SMTP, POP3, Autoload)

if __name__ == "__main__":
    main()
