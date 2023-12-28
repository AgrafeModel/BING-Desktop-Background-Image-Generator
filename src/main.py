from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ctypes
import os


SPI_SETDESKWALLPAPER = 20 #the code for setting the wallpaper
SPIF_UPDATEINIFILE = 0x01 #the code for updating the ini file
SPIF_SENDCHANGE = 0x02 #the code for sending a change

class BingImageScraper:
    def __init__(self, prompt):
        path = os.path.abspath("images")
        #check if the image folder exists
        if not os.path.exists(path):
            os.mkdir(path)
        print("Download path: " + path)



        self.PAGE_URL = "https://www.bing.com/create"
        self.PROMPT = prompt
        options = webdriver.EdgeOptions()
        options.use_chromium = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs",{
                'download.default_directory': path,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
        })
        #option of size
        self.driver = webdriver.Edge(options=options)
        #set the window size to very small
        self.driver.set_window_size(10, 10)
        #minimize the window
        self.driver.minimize_window()




        print("Scrapper initialized!")
        print("=====================================")
        print("Page URL: " + self.PAGE_URL)
        print("Prompt: " + self.PROMPT)
        print("=====================================")

        

    def open_page(self):
        self.driver.get(self.PAGE_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "create_btn_c"))
        )
            

        print("Page is ready!")

    def search_and_create_image(self):
        search_box = self.driver.find_element("id", "sb_form_q")
        #fully fill the search box character by character
        for i in self.PROMPT:
            search_box.send_keys(i)
            time.sleep(0.001)
        #click the create button
        create_btn = self.driver.find_element("id", "create_btn_c")
        create_btn.click()

    def wait_for_image_load(self):
        time_s = 0
        while True:
            try:
                self.img = self.driver.find_element("class name", "mimg")
                break
            except:
                time.sleep(1)
                time_s += 1
                if time_s % 15 == 0:
                    self.driver.refresh()
                    print("Page refreshed!")
                print("Waiting for the image to load...", time_s)
                continue
        print("Image is loaded!")
        
        #click of bnp_btn_reject
        try:
            self.driver.find_element("id", "bnp_btn_reject").click()
            print("Clicked the reject button!")
        except:
            print("No reject button!")


    def get_and_save_images(self):
        #get the 4 images, get the parent parent element, get the href, go to the href
        imgs=[]
        img = self.driver.find_elements("class name", "iusc") #the a tag
        for i in img:
            imgs.append(i.get_attribute("href"))
            print('Found image: ' + i.get_attribute("href"))
        #download the images
        for i in imgs:
            self.download_image(i)

    def download_image(self, url):
        print("Downloading image...", url)
        #go to the image page
        self.driver.get(url)
        time.sleep(1)
        #wait until we find the dld button
        while True:
            try:
                dld_btn = self.driver.find_element("class name", "dld")
                print("Found the dld button!")
                break
            except:
                print("Waiting for the dld button...")
                time.sleep(1)
                continue


        while True:
            try:
                #click the dld button
                dld_btn.click()
                print("Clicked the dld button!")
                break
            except:
                print("Waiting for the dld button...")
                self.reject()
                time.sleep(1)
                continue
        return True
    

    def reject(self):
        try:
            self.driver.find_element("id", "bnp_btn_reject").click()
            print("Clicked the reject button!")
        except:
            print("No reject button!")
    

    def set_wallpaper(self):
        print("Setting the wallpaper...")
        #go to projet root
        os.chdir("..")
        if not os.path.exists("save"):
            os.mkdir("save")
        #go to the images folder
        os.chdir("images")
        #get the name of a random image
        files = os.listdir()
        #get the number of files
        num_files = len(files)
        if(num_files == 0):
            print("No images found!")
            return False
        #get a random number
        rand_num = int(time.time()) % num_files
        #get the path of the image
        path = os.path.abspath(files[rand_num])
        #set the wallpaper
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print("Wallpaper set!")

    def move_to_save(self):
        print("Moving the image to the save folder...")
        os.chdir("images")
        #get all the files in it
        files = os.listdir()
        #move all the files to the save folder
        for i in files:
            os.rename(i, "../save/" + i)
        print("Moved the image to the save folder!")
        
        

    def close_browser(self):
        self.driver.quit()
        print("Browser closed!")

    def start(self):
        self.move_to_save()
        self.open_page()
        self.search_and_create_image()
        self.wait_for_image_load()
        self.get_and_save_images()
        self.set_wallpaper()
        self.close_browser()

    


if __name__ == "__main__":
    
    PROMPT = "An infinite tileable pattern. Black and white. Liquids"
    bing_scraper = BingImageScraper( PROMPT)
    bing_scraper.start()




