# CONVERSATION SCRIPT

## 👨🏾‍💻 Sending Phase

-   **Server:** <span style="color:yellow">220</span> Test Mail Server
-   **Client:** <span style="color:yellow">EHLO</span> server.com
-   **Server:** <span style="color:yellow">250</span> OK
-   **Client:** <span style="color:yellow">MAIL FROM:</span> \<sender@domain.com>
-   **Server:** <span style="color:yellow">250</span> sender \<sender@domain.com> OK
-   **Client:** <span style="color:yellow">RCPT TO:</span> \<receiver1@domain.com>
-   **Server:** <span style="color:yellow">250</span> recipient \<receiver1@domain.com> OK
-   **Client:** <span style="color:yellow">RCPT TO:</span> \<receiver2@domain.com>
-   **Server:** <span style="color:yellow">250</span> recipient \<receiver2@domain.com> OK
-   **Client:** <span style="color:yellow">RCPT TO:</span> \<receiver3@domain.com>
-   **Server:** <span style="color:yellow">250</span> recipient \<receiver3@domain.com> OK
-   **Client:** <span style="color:yellow">DATA</span>
-   **Server:** <span style="color:yellow">354</span> enter mail, end with line containing only "."
-   **Client:** 1st line of mail content
-   **Client:** 2nd line of mail content
-   **Client:** 3rd line of mail content
-   ...
-   ...
-   **Client:** Last line of mail content
-   **Client:** <span style="color:yellow">**.**</span>
-   **Server:** \<<span style="color:green">Total size of mail content</span>> bytes accepted
-   **Client:** <span style="color:yellow">QUIT</span>
-   **Server:** <span style="color:yellow">221</span> Closing connection

## 👨🏻‍💻 Receiving Phase
