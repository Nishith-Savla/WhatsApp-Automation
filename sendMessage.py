import os
import re
from time import sleep  # for stopping the program for an interval
from traceback import print_exc
from typing import List, Generator

import validators
# for controlling the browser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from urlextract import URLExtract

from conf import CHROMEDRIVER_PATH, CHROME_USER_DIR, EXTENSION_PATH


def draw_line(count: int = 100):
    """Draw a horizontal line of - count times

    Parameters
    ----------
    count
    """
    print("-" * count)


def extract_urls(text: List[str]) -> Generator:
    """Extracts urls from the text and returns a generator of all valid urls

    Parameters
    ----------
    text
        The text to extract urls from

    Yields
    ------
    url
        Valid urls from the text
    """
    extractor = URLExtract()
    for line in text:
        urls = extractor.find_urls(line)
        for url in urls:
            if validators.url(url):
                yield url


def _check_login(p_driver) -> bool:
    """Returns True if the user has successfully logged in to WhatsApp, else False"""
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().lstrip().startswith('yes'):
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


def _get_list(input_elem):
    if input_elem not in ('user_list', 'message'):
        raise Exception(f'Parameter (input_elem) should be either user_list or message! Rather {input_elem} was found')
    elem_to_choose = 'list of people' if input_elem.lower() == 'user_list' else 'message'
    choose_from_file = input("Do you want to choose the " + elem_to_choose + " from a file(Yes/No/Same as earlier): ")
    elements: List[str] = []  # Empty list for storing the elements

    if choose_from_file.lower().lstrip().startswith('same'):
        with open("temp_username_msg", "rb") as tempfile:
            retrieved_dict = eval(tempfile.read().decode())
            elements = retrieved_dict[input_elem]
    elif choose_from_file.lower().lstrip().startswith('yes'):
        filepath = input("Enter the file path: ")
        with open(filepath, "r", encoding='utf-8') as file:
            for line in file:
                elements.append(line.strip())
    else:
        if input_elem == 'user_list':
            elements = input("Enter the names of people you want to send the message to "
                             "(separated by commas if more than one): "
                             ).split(',')
            elements = [element.strip() for element in elements]
        else:
            elements = [input("Enter the message to send: ")]

    return elements


def connect(p_driver=None, options=None, driver_path=None):
    """Connects to whatsapp"""
    if p_driver is None:
        if driver_path is None:
            driver_path = input("Enter your driver path: ")
        pattern = re.compile(r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\];]:?)[\\]?"
                             r"([a-zA-Z0-9',.!@#$%^&()_+\-={}\[\];]+)[\\]?"
                             r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\]\\;]*)")
        match = pattern.match(driver_path)
        if match is not None:
            driver_path = match.group().replace('\\', '/')
        p_driver = webdriver.Chrome(driver_path, options=options)
    p_driver.get("https://web.whatsapp.com/")
    # Until login isn't successful, try checking and sleep for 2 seconds after every try
    while not _check_login(p_driver):
        sleep(2)
    return p_driver


def _take_input():
    # Taking the user names as input either from a file or from console by calling choose_from_file_input()
    user_list = _get_list('user_list')
    draw_line()

    # Taking the message as input either from a file or from console by calling choose_from_file_input()
    msg = _get_list('message')
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


def gather_input():
    user_list, message, send_count = _take_input()
    dict_to_write = dict(user_list=user_list, message=message)
    with open("temp_username_msg", "wb") as temp_file:
        temp_file.write(str(dict_to_write).encode())
    return user_list, message, send_count


def send(name, message, p_driver=None, count=1):
    """Sends the message to the user for 'count' number of times"""
    if p_driver is None:
        p_driver = webdriver.Chrome(CHROMEDRIVER_PATH)
    try:
        # Enter the name of the user in the search bar
        p_driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').clear()
        p_driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').send_keys(name)
        # Wait until the name is loaded and click on it after
        WebDriverWait(p_driver, 10).until(
            ec.presence_of_element_located((By.XPATH, '//span[@title = "{}"]'.format(name)))).click()

        # Find the message box / text area
        msg_box = p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        urls = extract_urls(message)
        for _ in range(count):
            for msg_line in message:  # iterate over the list of lines of a message
                msg_box.send_keys(msg_line + Keys.SHIFT + Keys.ENTER)
            if list(urls):
                try:
                    # Wait for 20 seconds until the link is loaded
                    WebDriverWait(p_driver, 20).until(
                        ec.presence_of_element_located((
                            By.XPATH, '//*[@id="main"]/footer/div[2]/div/div[5]/div[1]/div[1]/div')))
                except TimeoutException:
                    print("Couldn't load link preview")
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
    p_driver = connect(p_driver)

    while True:
        # Take all the inputs necessary for the send function
        user_list, message, send_count = gather_input()

        # Send message to each user in the list
        for user in user_list:
            send(user.strip(), message, p_driver, send_count)

        # Check if the user wants to logout from WhatsApp Web
        wanna_rerun = input("Do you want to send more messages(Yes/No): ")
        if wanna_rerun.lower().lstrip().startswith('no'):
            break

    wanna_quit = input("Do you want to logout (NOTE: This may stop sending any unsent "
                       "messages): ")
    if wanna_quit.lower().lstrip().startswith('yes'):
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/div').click()
        p_driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/span/div/ul/li[7]/div').click()

    # Remove the temporary files
    try:
        os.remove("temp_username_msg")
    except FileNotFoundError:
        pass
    except Exception:
        print_exc()


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
    except InvalidArgumentException:
        print("Couldn't load profile perhaps because another instance in running which is using the profile")
        driver.quit()
        options = webdriver.ChromeOptions()
        options.add_extension(EXTENSION_PATH)
        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

    # Here you can replace the path with your chromedriver path
    run(driver)
