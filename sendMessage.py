import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

def check_login():
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        try:
            driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            return True
        except:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            time.sleep(1.5)
            check_login()
    else:
        time.sleep(1.5)
        check_login()


option = webdriver.ChromeOptions()
driver = webdriver.Chrome("C:\\Users\\nishi\\chromedriver.exe")
driver.get("https://web.whatsapp.com/")

if check_login():
    user = input("Whom do you want to send the message to: ")
    found = False
    while not found:
        try:
            driver.find_element_by_xpath('//span[@title = "{}"]'.format(user)).click()
            found = True
            msg = input("Enter the message to send: ")
            msg_box = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
            count = int(input("How many times do you want to send the message: "))
            for i in range(count):
                msg_box.send_keys(msg)
                driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
        except NoSuchElementException:
            print(user + " not found")
