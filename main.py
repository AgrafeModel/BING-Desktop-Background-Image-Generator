from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ctypes
import os
from dotenv import load_dotenv
from yaspin import yaspin


SPI_SETDESKWALLPAPER = 20 #the code for setting the wallpaper
SPIF_UPDATEINIFILE = 0x01 #the code for updating the ini file
SPIF_SENDCHANGE = 0x02 #the code for sending a change

load_dotenv()

class BingImageScraper:
    def __init__(self, prompt,headless=True):
        
        self._start_msg()
        #--Create the images folder if it doesn't exist--#
        path = os.path.abspath("images")
        if not os.path.exists(path):
            os.mkdir(path)
        
        #--Initialize the variables--#
        self.PAGE_URL = "https://www.bing.com/create"
        self.PROMPT = prompt
        self.headless = headless

        #--Initialize the browser--#
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs",{
                'download.default_directory': path,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
        })
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " 
                             +
                            "(KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)

        
        print("=====================================")
        print("Page URL: " + self.PAGE_URL)
        print("Headless: " + str(self.headless))
        print('Prompt: ' + '\033[91m' + self.PROMPT + '\033[0m')
        print("=====================================")

    def _start_msg(self):
        print("\033[91m______ _            _____                _____                _             ")
        print("| ___ (_)          |_   _|              /  __ \\              | |            ")
        print("| |_/ /_ _ __   __ _ | | _ __ ___   __ _| /  \\/_ __ ___  __ _| |_ ___  _ __ ")
        print("| ___ \\ | '_ \\ / _` || || '_ ` _ \\ / _` | |   | '__/ _ \\/ _` | __/ _ \\| '__|")
        print("| |_/ / | | | | (_| || || | | | | | (_| | \\__/\\ | |  __/ (_| | || (_) | |   ")
        print("\\____/|_|_| |_|\\__, \\___/_| |_| |_|\\__, |\\____/_|  \\___|\\__,_|\\__\\___/|_|   ")
        print("               __/ |               __/ |                                    ")
        print("              |___/               |___/                                     ")
        print("                _____                                                      ")
        print("               /  ___|                                                     ")
        print("               \\ `--.  ___ _ __ __ _ _ __  _ __   ___ _ __                 ")
        print("                `--. \\/ __| '__/ _` | '_ \\| '_ \\ / _ \\ '__|                ")
        print("               /\\__/ / (__| | | (_| | |_) | |_) |  __/ |                   ")
        print("               \\____/ \\___|_|  \\__,_| .__/| .__/ \\___|_|                   ")
        print("                                    | |   | |                              ")
        print("                                    |_|   |_|                              ")
        print('\033[0m')

    def open_page(self):
        self.driver.get(self.PAGE_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "create_btn_c"))
        )
            

        print("Page is ready!")

    def search_and_create_image(self):
        try:
            print('-------Searching for the prompt-------')
            search_box = self.driver.find_element("id", "sb_form_q")
            #fully fill the search box character by character
            for i in self.PROMPT:
                search_box.send_keys(i)
            time.sleep(0.0001)

            ###click the create button
            create_btn = self.driver.find_element("id", "create_btn_c")
            create_btn.click()
            #wait and show now the url
            time.sleep(0.5)

            print("Page URL: " + self.driver.current_url)

            return True
        except Exception as e:
            print(e)
            return False
        

    def login_to_microsoft(self):
        print("-----------------Logging in to Microsoft-----------------")
        try:
            email_box = self.driver.find_element("id", "i0116")
            email_box.send_keys(os.getenv("MICROSOFT_EMAIL"))
            next_btn = self.driver.find_element("id", "idSIButton9")
            next_btn.click()
            time.sleep(0.5)
            password_box = self.driver.find_element("id", "i0118")
            password_box.send_keys(os.getenv("MICROSOFT_PASSWORD"))
            next_btn = self.driver.find_element("id", "idSIButton9")
            next_btn.click()
            time.sleep(0.5)
            stay_signed_in_btn = self.driver.find_element("id", "idSIButton9")
            stay_signed_in_btn.click()
            
            print("\033[92mLogged in to Microsoft!\033[0m")

            return True
        except Exception as e:
            print(e)
            return False
    
        

    def wait_for_image_load(self):
        print("-----------------Waiting for the images to load-----------------")

        if not self.driver.current_url.startswith("https://www.bing.com/images/create"):
            print("Not on the right page!")
            return False
        
        with yaspin(text="[/] Images are loading", color="yellow") as spinner:
            time_s = 0
            while True:
                try:
                    img = self.driver.find_element("class name", "mimg")
                    break
                except:
                    time.sleep(1)
                    time_s += 1
                    if time_s % 30 == 0:
                        print("~~~Refreshing the page~~~")
                        self.driver.refresh()

                    spinner.text = "[" + str(time_s) + "] Images are loading"
                    continue
        spinner.ok("✅")

        
        print("Image is loaded!")
        self.reject()


    def get_and_save_images(self):
        print("-----------------Getting and saving the images-----------------")
        imgs=[]
        img = self.driver.find_elements("class name", "iusc")
        for i in img:
            imgs.append(i.get_attribute("href"))
            print('Found image: ' + i.get_attribute("href"))

        for i in imgs:
            self.download_image(i)

    def download_image(self, url):
        print("-----------------Downloading the image-----------------")
        print("URL: " + url)
        self.driver.get(url)
        time.sleep(0.3)
        while True:
            try:
                dld_btn = self.driver.find_element("class name", "dld")
                print("Found the dld button!")
                dld_btn.click()
                break
            except Exception as e:
                print(e)
                self.reject()
                time.sleep(0.5)
                continue
        return True
    
    def reject(self):
        try:
            self.driver.find_element("id", "bnp_btn_reject").click()
            print("Clicked the reject button!")
        except:
            print("No reject button!")
    

    def set_wallpaper(self):
        print("-----------------Setting the wallpaper-----------------")
        try:
            if not os.path.exists("images"):
                os.chdir("..")
            os.chdir("images")
            files = os.listdir()
            num_files = len(files)
            if(num_files == 0):
                print("No images found!")
                return False

            rand_num = int(time.time()) % num_files

            path = os.path.abspath(files[rand_num])

            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
            print("Wallpaper n°" + str(rand_num) + " set!")
            print("\033[91m Check the images folder to see all the generated images! \033[0m")
            return True
        except Exception as e:
            print(e)
            return False

    def move_to_save(self):
        print("-----------------Moving the images to the save folder-----------------")

        if not os.path.exists("save"):
            os.mkdir("save")

        os.chdir("images")
        files = os.listdir()

        for i in files:
            os.rename(i, "../save/" + i)

        print("Moved the image to the save folder!")

    def save_prompt(self):
        print("-----------------Saving the prompt-----------------")
        os.chdir("..")
        if not os.path.exists("history.txt"):
            open("history.txt", "w").close()
        with open("history.txt", "a") as f:
            f.write(self.PROMPT + "\n")
        print("Saved the prompt!")

    def close_browser(self):
        print("-----------------Closing the browser-----------------")
        self.driver.quit()

    def start(self):
        self.move_to_save()
        self.save_prompt()
        self.open_page()
        self.search_and_create_image()

        if self.headless:
            self.login_to_microsoft()
        
        self.wait_for_image_load()
        self.get_and_save_images()
        self.set_wallpaper()
        self.close_browser()

    


if __name__ == "__main__":
    print("=====================================")
    PROMPT = "An infinite tileable pattern. "
    print("Default prompt parameter: " + PROMPT)
    PROMPT += input("\033[91mEnter the prompt: \033[0m")
    print("=====================================")
    bing_scraper = BingImageScraper(PROMPT)
    bing_scraper.start()






