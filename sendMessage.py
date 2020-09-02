import re
from time import sleep  # for stopping the program for an interval
from traceback import print_exc
from typing import List

# for controlling the browser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from conf import CHROMEDRIVER_PATH, CHROME_USER_DIR, EXTENSION_PATH


def draw_line(count=100):
    """Draw a horizontal line of - count times"""
    print("-" * count)


def check_login(p_driver) -> bool:
    """Returns True if the user has successfully logged in to WhatsApp, else False"""
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        # noinspection PyBroadException
        try:
            # Check if any element (here, profile pic) is present
            p_driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            draw_line()
            return True
        except NoSuchElementException:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            draw_line()
    return False


def choose_from_file_input(input_elem):
    if input_elem not in ('username', 'message'):
        raise Exception(f'Parameter (input_elem) should be either username or message! Rather {input_elem} was found')
    elem_to_choose = 'list of people' if input_elem.lower() == 'username' else 'message'
    choose_from_file = input("Do you want to choose the " + elem_to_choose + " from a file: ")
    elements: List[str] = []  # Empty list for storing the elements

    if choose_from_file.lower().startswith("yes"):
        filepath = input("Enter the file path: ")
        with open(filepath, "r", encoding='utf-8') as file:
            for line in file:
                elements.append(line.strip())
    else:
        elements = input("Enter the names of people you want to send the message to "
                         "(separated by ', ' if more than one): "
                         ).split(', ') if input_elem == 'username' else [input("Enter the message to send: ")]

    return elements


def take_input():
    # Taking the user names as input either from a file or from console by calling choose_from_file_input()
    user_list = choose_from_file_input('username')
    draw_line()

    # Taking the message as input either from a file or from console by calling choose_from_file_input()
    msg = choose_from_file_input('message')
    draw_line()

    # Unless a valid count isn't given
    while True:
        try:
            send_count = int(input("How many times do you want to send the message: "))
            if send_count < 1:
                raise ValueError
            break
        except ValueError:
            print("Please enter a positive integer ")
    draw_line()

    return user_list, msg, send_count


def send(p_driver, name, message, count=1):
    """Sends the message to the user for 'count' number of times"""
    try:
        # Enter the name of the user in the search bar
        p_driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').send_keys(name)
        # Wait until the name is loaded and click on it after
        WebDriverWait(p_driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//span[@title = "{}"]'.format(name)))).click()

        # Find the message box / text area
        msg_box = p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for _ in range(count):
            for msg_line in message:  # iterate over the list of lines of a message
                msg_box.send_keys(msg_line + Keys.SHIFT + Keys.ENTER)
            sleep(1)
            # Click on the send button (alternatively you can also pass the enter key to the message box)
            p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()

    except NoSuchElementException:
        print(name + " not found")
    except Exception:
        print_exc()
    finally:
        p_driver.implicitly_wait(5)


def run(p_driver=None):
    """Runs the whole program by calling the send function"""
    if p_driver is None:
        chromedriver_path = input("Enter your chrome driver path: ")
        pattern = re.compile(r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\];]:?)[\\]?"
                             r"([a-zA-Z0-9',.!@#$%^&()_+\-={}\[\];]+)[\\]?"
                             r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\]\\;]*)")
        match = pattern.match(chromedriver_path)
        if match is not None:
            chromedriver_path = match.group().replace('\\', '/')
        p_driver = webdriver.Chrome(chromedriver_path)

    p_driver.get("https://web.whatsapp.com/")
    # Until login isn't successful, try checking and sleep for 2 seconds after every try
    while not check_login(p_driver):
        sleep(2)

    # Take all the inputs necessary for the send function
    user_list, msg, send_count = take_input()

    # Send message to each user in the list
    for user in user_list:
        send(p_driver, user.strip(), msg, send_count)

    # Check if the user wants to logout from WhatsApp Web
    wanna_quit = input("Do you want to logout (NOTE: This may stop sending any unsent "
                       "messages): ")
    if wanna_quit.lower().startswith("yes"):
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/div').click()
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/span/div/ul/li[7]/div').click()


# Initializing driver variable for scope resolution
driver = None

if __name__ == '__main__':
    # Chrome options
    options = webdriver.ChromeOptions()
    # You can add extensions to the browser by passing its path here
    options.add_extension(EXTENSION_PATH)
    # Loading cache from user profile for decreasing frequency of scanning
    # For windows
    try:
        options.add_argument(f"user-data-dir={CHROME_USER_DIR}")
        options.add_argument("profile-directory=Default")
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
    except Exception:
        print("Couldn't load profile perhaps because another instance in running which is using the profile")
        options = webdriver.ChromeOptions()
        options.add_extension(EXTENSION_PATH)
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    # Here you can replace the path with your chromedriver path
    run(driver)
