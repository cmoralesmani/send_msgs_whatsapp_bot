from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import chromedriver_binary
import csv
import sys
import time
import pyperclip


class BotWhatsapp:
    def __init__(self):
        self.base_url = 'https://web.whatsapp.com/'
        self.timeout = 30
        self.msgs = self.__read_csv('resources/msgs.csv')
        print("Mensajes: ", self.msgs)
        self.targets = self.__read_csv('resources/contacts.csv')
        print("Destinos: ", [target for target in self.targets])
        self.__set_paths()
    
    def __read_csv(self, filename):
        results = []
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                results.append(row)
        return results

    def __set_paths(self):
        self.search_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
        self.input_xpath = '//div[@contenteditable="true"][@data-tab="6"]'
        self.contact_xpath = '//span[@title="{0}"]' # Hay que pasarle con .format() el contacto
        self.first_contact = '//*[@id="pane-side"]/div[1]/div/div/div[1]' 
    
    def __start_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--profile-directory=Default')
        options.add_argument("--disable-plugins-discovery")

        # Se utiliza si hay que utilizar el driver de algun lugar especifico
        # pero en este caso estamos utilizando el paquete chromedriver_binary para cargar el driver

        # self.browser = webdriver.Chrome(executable_path=self.path_driver,
        #                                 chrome_options=options)
        self.browser = webdriver.Chrome(options=options)
        self.browser.maximize_window()
        self.browser.get(self.base_url)
        try:
            # wait = WebDriverWait(driver, 10)
            self.wait5 = WebDriverWait(self.browser, 5)
            input("Escanea el código QR y presiona Enter")
            self.wait5.until(
                EC.presence_of_element_located((By.XPATH, self.search_xpath))
            )
            return True
        except Exception as e:
            print(e)
            return False
    
    def send_messages(self):
        start = self.__start_browser()
        if not start:
            return False
        
        for contact in self.targets:
            user_search = self.__search_user_or_group(contact["nombre"])
            if not (user_search or contact or message):
                return False

            for msg_to in self.msgs:
                message = msg_to["mensaje"].strip()
                try:
                    input_box = self.wait5.until(
                        EC.presence_of_element_located(
                            (By.XPATH, self.input_xpath)
                        )
                    )
                except Exception as e:
                    print(e)
                    return
                messages = message.split("\\n")
                
                for i in range(int(msg_to["cantidad"])):
                    for msg in messages:
                        pyperclip.copy(msg)
                        input_box.send_keys(Keys.SHIFT, Keys.INSERT)
                        input_box.send_keys(Keys.SHIFT + Keys.ENTER)
                    
                    time.sleep(2)
                    input_box.send_keys(Keys.ENTER)
                print(f'Mensajes enviado a {contact["nombre"]}.')
        return True
    
    def quit_browser(self):
        self.browser.quit()
    
    def __search_user_or_group(self, contact):
        # Select the target
        search_box = self.wait5.until(
            EC.presence_of_element_located((By.XPATH, self.search_xpath))
        )
        search_box.clear()
        time.sleep(1)
        pyperclip.copy(contact)

        search_box.send_keys(Keys.SHIFT, Keys.INSERT)
        print(f"El contacto {contact} se seleccionó correctamente")

        try:
            vali_ = self.wait5.until(
                EC.presence_of_element_located(
                    (By.XPATH, self.first_contact)
                )
            )
            if vali_.is_displayed():
                search_box.send_keys(Keys.ENTER)
                return True
        except Exception as e:
            print(e)
            print(f'No se encontró el contacto {contact}.')
        return False

obj = BotWhatsapp()
obj.send_messages()
# obj.quit_browser()
