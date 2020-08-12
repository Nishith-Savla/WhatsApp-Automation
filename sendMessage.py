from time import sleep  # for stopping the program for an interval
from typing import List

# for controlling the browser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def check_login(p_driver) -> bool:
    """Returns True if the user has successfully logged in to WhatsApp, else False
    :return True or False
    """
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        # noinspection PyBroadException
        try:
            p_driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            return True
        except NoSuchElementException:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            return False
    else:
        return False


def send(p_driver, name, message, count=1):
    """Sends the message to the user for 'count' number of times"""
    try:
        p_driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').send_keys(name)
        WebDriverWait(p_driver, 20).until(
            ec.presence_of_element_located((By.XPATH, '//span[@title = "{}"]'.format(name)))).click()
        msg_box = p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for i in range(count):
            for msg_line in message:
                msg_box.send_keys(msg_line + Keys.SHIFT + Keys.ENTER)
            p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
    except Exception:
        print(name + " not found")
    finally:
        p_driver.implicitly_wait(5)


def run(p_driver):
    """Runs the whole program"""
    p_driver.get("https://web.whatsapp.com/")
    while not check_login(p_driver):
        sleep(2)

    choose_from_file = input("Do you want to choose the list of people from a file: ")
    user_list = []
    if choose_from_file.lower().startswith("yes"):
        filepath = input("Enter the file path: ")
        with open(filepath, "r") as file:
            for line in file:
                user_list.append(line)
    elif choose_from_file.lower().startswith("no"):
        names = input(
            "Enter the names of people you want to send the message to (separated by ', ' if more than one): ")
        user_list = names.split(', ')

    msg: List[str] = []
    choose_from_file = input("Do you want to choose the message from a file: ")
    if choose_from_file.lower().startswith("yes"):
        filepath = input("Enter the file path: ")
        with open(filepath, "r") as file:
            for line in file:
                msg.append(line.rstrip())
    elif choose_from_file.lower().startswith("no"):
        msg = [input("Enter the message to send: ")]

    send_count = int(input("How many times do you want to send the message: "))

    for user in user_list:
        send(p_driver, user.lstrip().rstrip(), msg, send_count)

    wanna_quit = input("Do you want to logout (NOTE: This may stop sending any unsent "
                       "messages): ")
    if wanna_quit.lower().startswith("yes"):
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/div').click()
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/span/div/ul/li[7]/div').click()
        p_driver.quit()


# Chrome options
option = webdriver.ChromeOptions()
# You can add extensions to the browser by passing its path here
option.add_extension("EXTENSION PATH, IF ANY")
driver = webdriver.Chrome("CHROMEDRIVER PATH", options=option)
if __name__ == "__main__":
    run(driver)
