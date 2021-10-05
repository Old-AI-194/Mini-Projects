import pandas as pd
from csv import writer
import datetime
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys


class Crawl:
    def __init__(self, symbol_list, csv_dir, chrome_dir, username, password):
        """
        Parameters:
        symbol_list - List cac symbol lay data (["VN30F1M", "VN30F2M", ....]) - dang list chua cac str
        csv_dir - Duong dan den thu muc chua cac file luu du lieu - dang str
        chrome_dir - Duong dan den file chromedriver.exe  - dang str
        username - Ten dang nhap account Vndirect - dang str
        password - Mat khau account Vndirect - dang str
        """
        self.symbol_list = symbol_list
        self.csv_dir = csv_dir
        self.username = username
        self.password = password
        self.data_dict = dict((x,y) for x, y in [(z, []) for z in symbol_list])
        self.csv_data = dict((k, v) for k, v in [(s, None) for s in symbol_list])

        self.xpath_dict = {'Symbol': ['VN30F1M', 'VN30F2M', 'VN30F1Q', 'VN30F2Q'],
                      'Bid': ['//*[@id="banggia-phaisinh-body"]/tr[1]/td[12]',
                              '//*[@id="banggia-phaisinh-body"]/tr[2]/td[12]',
                              '//*[@id="banggia-phaisinh-body"]/tr[3]/td[12]',
                              '//*[@id="banggia-phaisinh-body"]/tr[4]/td[12]'],
                      'Ask': ['//*[@id="banggia-phaisinh-body"]/tr[1]/td[17]',
                              '//*[@id="banggia-phaisinh-body"]/tr[2]/td[17]',
                              '//*[@id="banggia-phaisinh-body"]/tr[3]/td[17]',
                              '//*[@id="banggia-phaisinh-body"]/tr[4]/td[17]'],
                      'Bid_vol': ['//*[@id="banggia-phaisinh-body"]/tr[1]/td[13]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[2]/td[13]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[3]/td[13]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[4]/td[13]'],
                      'Ask_vol': ['//*[@id="banggia-phaisinh-body"]/tr[1]/td[18]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[2]/td[18]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[3]/td[18]',
                                  '//*[@id="banggia-phaisinh-body"]/tr[4]/td[18]']}
        self.xpath_df = pd.DataFrame(self.xpath_dict).set_index('Symbol')

        self.browser = webdriver.Chrome(executable_path = chrome_dir)
        self.web_access()
        sleep((datetime.datetime.now().replace(hour=9, minute=0, second=2) - datetime.datetime.now()).seconds)
        self.save_data()

    #Ham dung de truy cap bang gia
    def web_access(self):

        self.browser.get("https://trade.vndirect.com.vn/chung-khoan/phai-sinh")
        sleep(6)
        # Dang nhap vao trang web
        txtUser = self.browser.find_element_by_xpath('//*[@id="login-popup"]/form/div[1]/div/input')
        txtUser.send_keys(self.username)
        txtPass = self.browser.find_element_by_xpath('//*[@id="login-popup"]/form/div[2]/div/input')
        txtPass.send_keys(self.password)
        txtPass.send_keys(Keys.ENTER)
        sleep(6)
        # Truy cap bang gia phai sinh
        phaisinh_link = self.browser.find_element_by_xpath('//*[@id="nav"]/ul[1]/li[6]/a')
        phaisinh_link.click()
        sleep(6)

    #Ham cao va luu du lieu
    def save_data(self):
        #Tao va mo file csv
        for x in self.symbol_list:
            self.csv_data[x] = open(self.csv_dir + x + '.csv', 'a')

        while datetime.datetime.now().time() < datetime.time(hour=14, minute=30):
            for s in self.symbol_list:
                priod_data = self.data_dict[s][1:]
                new_data = []
                dt = datetime.datetime.now()
                for d in ['Bid', 'Ask', 'Bid_vol', 'Ask_vol']:
                    new_data.append(self.browser.find_element_by_xpath(self.xpath_df.loc[s, d]).text)
                if new_data != priod_data and new_data[0] != 'ATO' and new_data[0] != 'ATC' \
                        and datetime.time(hour=9, minute=0) < datetime.datetime.now().time():
                    self.data_dict[s] = [dt] + new_data
                    writer(self.csv_data[s]).writerow(self.data_dict[s])
                    print(s + ": " + self.data_dict[s][1] + '|' + self.data_dict[s][2])
                    #self.csv_data[s].close()
        if datetime.datetime.now().time() >= datetime.time(hour=14, minute=30):
            for z in self.csv_data:
                self.csv_data[z].close()


if __name__ == "__main__":
    symbol_list = ['VN30F1M', 'VN30F2M', 'VN30F1Q', 'VN30F2Q']
    csv_dir = 'D:/BA Future/'
    chrome_dir = "D:/chromedriver_win32/chromedriver.exe"
    username = '0001582696'
    password = 'manhtien194'

    crawl = Crawl(symbol_list, csv_dir, chrome_dir, username, password)