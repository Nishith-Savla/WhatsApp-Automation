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


def draw_line(count=100):
    """Draw a horizontal line of - count times"""
    print("-" * count)


def check_login(p_driver) -> bool:
    """Returns True if the user has successfully logged in to WhatsApp, else False"""
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        # noinspection PyBroadException
        try:
            # Check if any element (here profile pic) is present
            p_driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            draw_line()
            return True
        except NoSuchElementException:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            draw_line()
            return False
    else:
        return False


def take_input():
    # Taking the user names as input either from a file or from console
    choose_from_file = input("Do you want to choose the list of people from a file: ")
    user_list: List[str] = []  # Empty list for storing names of receivers

    if choose_from_file.lower().startswith("yes"):
        filepath = input("Enter the file path: ")
        with open(filepath, "r", encoding='utf-8') as file:
            for line in file:
                user_list.append(line)
    else:
        names = input(
            "Enter the names of people you want to send the message to (separated by ', ' if more than one): ")
        user_list = names.split(', ')

    draw_line()

    # Taking the message as input either from a file or from console
    msg: List[str] = []  # Empty list for storing message lines
    choose_from_file = input("Do you want to choose the message from a file: ")

    if choose_from_file.lower().startswith("yes"):
        filepath = input("Enter the file path: ")
        with open(filepath, "r", encoding='utf-8') as file:
            for line in file:
                msg.append(line.rstrip())
    else:
        msg = [input("Enter the message to send: ")]
    draw_line()

    # Unless a valid count isn't given
    while True:
        try:
            send_count = int(input("How many times do you want to send the message: "))
            if send_count < 1:
                raise Exception
            break
        except Exception:
            print("Please enter a positive integer ")

    draw_line()

    return user_list, msg, send_count


def send(p_driver, name, message, count=1):
    """Sends the message to the user for 'count' number of times"""
    try:
        # Script to execute for sending emojis
        js_add_text_to_input: str = '''
          var elm = arguments[0], txt = arguments[1];
          elm.value += txt;
          elm.dispatchEvent(new Event('change'));
          '''
        # Enter the name of the user in the search bar
        search_bar = p_driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]')

        # To send emojis to the search bar which chromedriver doesn't support
        p_driver.execute_script(js_add_text_to_input, search_bar, name)

        # Wait until the name is loaded and click on it after
        WebDriverWait(p_driver, 20).until(
            ec.presence_of_element_located((By.XPATH, '//span[@title = "{}"]'.format(name)))).click()

        # Find the message box / text area
        msg_box = p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for i in range(count):
            for msg_line in message:  # iterate over the list of lines of a message
                msg_box.send_keys(msg_line + Keys.SHIFT + Keys.ENTER)
            # Click on the send button (alternatively you can also pass the enter key to the message box)
            p_driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
    except NoSuchElementException:
        print(name + " not found")
    except Exception:
        print_exc()
    finally:
        p_driver.implicitly_wait(5)


def run(p_driver=None):
    if p_driver is None:
        chromedriver_path = input("Enter your chrome driver path: ")
        pattern = re.compile(r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\];]:?)[\\]?"
                             r"([a-zA-Z0-9',.!@#$%^&()_+\-={}\[\];]+)[\\]?"
                             r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\]\\;]*)")
        match = pattern.match(chromedriver_path)
        if match is not None:
            chromedriver_path = match.group().replace('\\', '/')
        print(chromedriver_path)
        p_driver = webdriver.Chrome(chromedriver_path)
    """Runs the whole program by calling the send function"""
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
    option = webdriver.ChromeOptions()
    # You can add extensions to the browser by passing its path here
    option.add_extension("D:/Extensions/extension_4_9_16_0.crx")
    # Loading cache from user profile for decreasing frequency of scanning
    # For windows
    try:
        option.add_argument(  # Here you can replace the user name('nishi') with yours
            "--user-data-dir=C:/Users/nishi/AppData/Local/Google/Chrome/User\ Data/Default")
        option.add_argument("--profile-directory=Default")
    except Exception:
        print("Couldn't load profile perhaps because another instance in running which is using the profile")

    # Here you can replace the path with your chromedriver path
    driver = webdriver.Chrome("C:/Users/nishi/chromedriver.exe", options=option)
    run(driver)
