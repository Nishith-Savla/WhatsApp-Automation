import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def check_login() -> bool:
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        # noinspection PyBroadException
        try:
            driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            return True
        except NoSuchElementException:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            return False
        except Exception:
            print(Exception)
            return False
    else:
        return False


def send_to_everyone(name, message, count):
    try:
        driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').send_keys(name)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@title = "{}"]'.format(name)))).click()
        msg_box = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for i in range(count):
            msg_box.send_keys(message)
            driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
    except NoSuchElementException:
        print(name + " not found")
    finally:
        driver.implicitly_wait(5)


option = webdriver.ChromeOptions()
driver = webdriver.Chrome("C:\\Users\\nishi\\chromedriver.exe")
driver.get("https://web.whatsapp.com/")

while not check_login():
    time.sleep(2)

choose_from_file = input("Do you want to choose the list of people from a file: ")
user_list = []
if choose_from_file.lower().startswith("yes"):
    filepath = input("Enter the file path: ")
    file = open(filepath, "r")
    for line in file:
        line = line.rstrip()
        user_list.append(line)
elif choose_from_file.lower().startswith("no"):
    names = input("Enter the names of people you want to send the message to (separated by ', ' if more than one): ")
    user_list = names.split(', ')

msg = input("Enter the message to send: ")
send_count = int(input("How many times do you want to send the message: "))

for user in user_list:
    if user.endswith(' '):
        user.rstrip(' ')
    send_to_everyone(user, msg, send_count)

driver.quit()
