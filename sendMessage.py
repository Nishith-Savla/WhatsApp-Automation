from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_login():
    is_connected = input("Have you signed in WhatsApp web? (Yes/No): ")
    if is_connected.lower().startswith('yes'):
        try:
            driver.find_element_by_xpath('//*[@id="side"]/header/div[1]/div/img')
            print("Login successful")
            return True
        except NoSuchElementException:
            print("It doesn't seem you have logged in")
            print('Try logging in again')
            return False
        except:
            return False
    else:
        check_login()


option = webdriver.ChromeOptions()
driver = webdriver.Chrome("C:\\Users\\nishi\\chromedriver.exe")
driver.get("https://web.whatsapp.com/")

while not check_login():
    driver.implicitly_wait(2)

user = input("Whom do you want to send the message to: ")
try:
    driver.find_element_by_xpath('//*[@id="side"]/div[1]/div/label/div/div[2]').send_keys(user)
    x_path = '//span[@title = "{}"]'.format(user)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, x_path))).click()
    msg = input("Enter the message to send: ")
    msg_box = driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
    count = int(input("How many times do you want to send the message: "))
    for i in range(count):
        msg_box.send_keys(msg)
        driver.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[3]/button').click()
except NoSuchElementException:
    print(user + " not found")
finally:
    driver.quit()
