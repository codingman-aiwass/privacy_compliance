from selenium.webdriver.chrome.options import Options
import time
import chardet
from bs4 import BeautifulSoup
from selenium import webdriver
class Createdriver():
    driver = None
    def __init__(self):
        if Createdriver.driver is None:
            self.driver = self.browser()
            Createdriver.driver = self.driver
        else:
            self.driver  = Createdriver.driver
    def browser(self):
        #currentPath = os.getcwd().replace('\\', '/')
        #cmd = [currentPath + "/chrome.bat"]
        #subprocess.Popen(cmd)
        #options = webdriver.ChromeOptions()

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-popup-blocking")

        # options = Options()
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        return driver
class Privacypolicy(Createdriver):
    def get_privacypolicy_html(self,url):
        '''
        :param url: 隐私政策网址
        :return: 返回html页面源码内容
        '''
        soup = None
        try:
            self.driver.get(url)
            self.driver.set_page_load_timeout(4)
            self.driver.set_script_timeout(4)
            time.sleep(1.5)
            html = self.driver.page_source
            soup = BeautifulSoup(html,'html.parser')
            #print(self.driver.page_source)
            #self.quit_html()
        except TimeoutError:
            print("页面请求超时")
        except Exception as e:
            print(e)

        return soup
    def get_html_encoding(self,html):
        '''
        :param html:网页源码
        :return:返回编码方式如'utf-8'
        '''
        result = chardet.detect(html)['encoding']
        return result
    def close_html(self):
        '''
        :return: 关闭当前页
        '''
        self.driver.close()
    def quit_html(self):
        '''
        :return: 关闭所有页
        '''
        self.driver.quit()
driver = Privacypolicy()