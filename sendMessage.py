"""WhatsApp Message Sender API."""
import re
from time import sleep  # for stopping the program for an interval
from traceback import print_exc
from typing import List, Generator

import validators
# for controlling the browser
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from urlextract import URLExtract

from conf import CHROME_USER_DIR, EXTENSION_PATH, CHROMEDRIVER_PATH


class WhatsappSender:
    def __init__(self, driver=None, user_list=None, message=None):
        self.user_list = user_list
        self.message = message
        self.driver = driver
        self.send_count = 0
        self.__connection_established = False
        self.load_url_preview = False
        self.force_take_input = False

    @staticmethod
    def draw_line(character: str = '-', count: int = 100):
        """Draw a horizontal line of - count times.

        Parameters
        ----------
        character
            Character to print.
        count
            Number of times to print the character.
        """
        print(character * count)

    # TODO decide whether to keep this static or not
    @staticmethod
    def __extract_urls(text: List[str]) -> Generator:
        """Extract urls from the text and returns a generator of all valid urls.

        Parameters
        ----------
        text
            The text to extract urls from.

        Yields
        ------
        url
            Valid urls from the text.
        """
        extractor = URLExtract()
        for line in text:
            urls = extractor.find_urls(line)
            for url in urls:
                if validators.url(url):
                    yield url

    def _check_login(self) -> bool:
        """Return True if the user has successfully logged in to WhatsApp."""
        is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
        if is_connected.lower().lstrip().startswith('yes'):
            # noinspection PyBroadException
            try:
                # Check if any element (here, profile pic) is present
                self.driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
                print("Login successful")
                self.draw_line()
                return True
            except NoSuchElementException:
                print("It doesn't seem you have logged in")
                print('Try logging in again')
                self.draw_line()
        return False

    def __get_list(self, input_elem):
        """Get the list i.e. {input_elem}s from the user or the file.

        Parameters
        ----------
        input_elem : str
            Should be 'user_list' / 'message'.
        """
        assert input_elem in ('user_list', 'message'), \
            f'Parameter (input_elem) should be either user_list or message! Rather {input_elem} was found'
        elem_to_choose = 'list of people' if input_elem == 'user_list' else 'message'
        choose_from_file = input(
            "Do you want to choose the " + elem_to_choose + " from a file(Yes/No/Same as earlier): ")
        elements: List[str] = []  # Empty list for storing the elements

        if choose_from_file.lower().lstrip().startswith('same'):
            assert self.user_list, "User list is empty"
            assert self.message, "Message is empty"
        elif choose_from_file.lower().lstrip().startswith('yes'):
            filepath = input("Enter the file path: ")
            with open(filepath, "r", encoding='utf-8') as file:
                for line in file:
                    elements.append(line.strip())
            if input_elem == 'user_list':
                self.user_list = elements
            else:
                self.message = elements
        else:
            if input_elem == 'user_list':
                self.user_list = input("Enter the names of people you want to send the message to "
                                       "(separated by commas if more than one): "
                                       ).split(',')
                self.user_list = [user.strip() for user in self.user_list]
            else:
                self.message = [input("Enter the message to send: ")]

    def connect(self, options=None, driver_path=None):
        """Connect to whatsapp."""
        if not self.driver:
            if not driver_path:
                driver_path = input("Enter your driver path: ")
            pattern = re.compile(r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\];]:?)[\\]?"
                                 r"([a-zA-Z0-9',.!@#$%^&()_+\-={}\[\];]+)[\\]?"
                                 r"([a-zA-z0-9',.!@#$%^&()_+\-={}\[\]\\;]*)")
            match = pattern.match(driver_path)
            if match:
                driver_path = match.group().replace('\\', '/')
            self.driver = webdriver.Chrome(executable_path=driver_path, options=options)
        self.driver.get("https://web.whatsapp.com/")
        # Try checking until login isn't successful and sleep for 2 seconds after every try
        while not self._check_login():
            sleep(2)

    def get_input(self, force_take_input=False):
        """Take the user names as input from file or from console by calling __get_list()."""
        if force_take_input or not self.user_list:
            self.__get_list('user_list')
            self.draw_line()

        if force_take_input or not self.message:
            self.__get_list('message')
            self.draw_line()

        # Unless a valid count isn't given
        if force_take_input or not self.send_count:
            while True:
                try:
                    self.send_count = int(input("How many times do you want to send the message: "))
                    assert self.send_count > 0, "Send Count must be greater than 0!"
                    break
                except ValueError:
                    print("Please enter a positive integer.")
            self.draw_line()

        # TODO add a better if
        if force_take_input or not self.load_url_preview:
            wanna_load_url_preview = input("Do you want to load URL preview(Yes/No): ")
            if wanna_load_url_preview.lower().lstrip().startswith('yes'):
                self.load_url_preview = True

    def send_message(self, name, message, count=1):
        """Send the message to the user for 'count' number of times."""
        try:
            # Enter the name of the user in the search bar
            search_box = self.driver.find_element_by_xpath(
                '//div[contains(text(), "Search")]/following-sibling::label//div[@contenteditable="true"]')
            search_box.clear()
            search_box.send_keys(name + Keys.ENTER)

            # Find the message box / text area
            msg_box = self.driver.find_element_by_xpath(
                '//div[contains(text(), "message")]/following-sibling::div[@contenteditable="true"]')

            # Load URLs only if load_url_preview is set to True
            urls = []
            if self.load_url_preview:
                urls = self.__extract_urls(message)

            for _ in range(count):
                for msg_line in message:  # iterate over the list of lines of a message
                    msg_box.send_keys(msg_line + Keys.SHIFT + Keys.ENTER)
                if list(urls):
                    try:
                        WebDriverWait(self.driver, 20).until(  # Wait for 20 seconds until the url preview is loaded
                            ec.presence_of_element_located((By.XPATH, '//footer/div[2]/div//div[@title]')))
                    except TimeoutException:
                        print("Couldn't load url preview")
                # Send the enter key to the message box
                # (alternatively you can also Click on the send button)
                # self.driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
                msg_box.send_keys(Keys.ENTER)
        except NoSuchElementException:
            print(name + " not found")
        except Exception:
            print_exc()
        finally:
            self.driver.implicitly_wait(5)

    def run(self):
        """Run the whole program by calling the send_message function."""
        while True:
            # Take all the necessary inputs
            self.get_input(self.force_take_input)
            # Send message to each user in the list
            for user in self.user_list:
                self.send_message(user.strip(), self.message, self.send_count)

            # Check if the user wants to logout from WhatsApp Web
            wanna_rerun = input("Do you want to send more messages(Yes/No): ")
            if wanna_rerun.lower().lstrip().startswith('no'):
                break
            self.force_take_input = True

        wanna_quit = input("Do you want to logout (NOTE: This may stop sending any unsent "
                           "messages): ")
        if wanna_quit.lower().lstrip().startswith('yes'):
            self.driver.find_element_by_xpath('//*[@id="side"]/header/div[2]/div/span/div[3]/div').click()
            self.driver.find_element_by_xpath(
                '//*[@id="side"]/header/div[2]/div/span/div[3]/span/div/ul/li[7]/div').click()


if __name__ == '__main__':
    # Chrome options
    options = webdriver.ChromeOptions()
    # You can add extensions to the browser by passing its path here
    options.add_extension(EXTENSION_PATH)
    # Loading cache from user profile for decreasing frequency of scanning
    # For windows
    options.add_argument(f"user-data-dir={CHROME_USER_DIR}")
    options.add_argument("profile-directory=Default")
    # TODO add handler if profile is open
    # Here you can replace the path with your chromedriver path
    whatsapp_sender = WhatsappSender()
    whatsapp_sender.connect(options=options, driver_path=CHROMEDRIVER_PATH)
    whatsapp_sender.get_input()
    whatsapp_sender.run()
