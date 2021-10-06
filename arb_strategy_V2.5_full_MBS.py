import ast
import datetime
from time import sleep

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class Trading:
    def __init__(self, symbol_list, chrome_dir, profit, fee, MA_priod, over_tp, acc_list, import_log,
                 zone_len):
        """
        Parameters:
        symbol_list - List 2 symbol (["VN30F1M", "VN30F2M"]) - dang list chua cac str
        chrome_dir - Duong dan den file chromedriver.exe  - dang str
        vnd_acc - List acc va pass dang nhap Vndirect (['used_name', 'password']) - dang list chua 2 str
        profit - So point du kien muon dat duoc - dang float
        fee - Luong point phi du kien - dang float
        MA_priod - Ky cua duong SMA - dang int
        over_tp - List cac point khi gia cat qua duong MA sau do dong lenh ([1.5,1,0.5] - dang float
        csv_dir - Duong dan den file chua du lieu - dang str
        acc_list - List acc va pass dang nhap 2 acc vps ([['used_name1', 'password1'],['used_name2', 'password2']]
        - dang list chua list chua str
        import_log - chon de nap data giao dich tu temp_log hay khong, import_log = 1 la co, con lai thi khong
        zone_len - do rong vung ma diff co the giao dong ben trong ma khong bi huy lenh - dang float
        """
        self.symbol_list = symbol_list
        self.profit = profit
        self.fee = fee
        self.MA_priod = MA_priod
        self.over_tp = over_tp
        self.acc_list = acc_list
        self.zone_len = zone_len

        # Add data tu file log
        if import_log == 1:
            log = open("D:/temp_log.txt", "r")
            ls = log.readlines()
            l1 = ls[0][:-1]
            l2 = ls[1][:-1]
            l3 = ls[2][:-1]
            l4 = ls[3]
            self.diff = ast.literal_eval(l1)
            self.position = ast.literal_eval(l2)
            self.target = ast.literal_eval(l3)
            self.id_list = ast.literal_eval(l4)
            log.close()
        else:
            self.diff = [[0.0], [0.0]]
            self.position = [[0 for x in self.over_tp], [0 for x in self.over_tp]]
            self.target = [[0.0 for y in self.over_tp], [0.0 for y in self.over_tp]]
            self.id_list = []

        self.MA = [0.0, 0.0]
        self.time_now = None
        self.last_time_second = 0
        self.order_price = [[0.0 for p in self.over_tp], [0.0 for p in self.over_tp]]
        self.id_cancel = [['' for z in self.over_tp], ['' for z in self.over_tp]]

        self.ask_x = 0.0
        self.bid_x = 0.0
        self.bid_y = 0.0
        self.ask_y = 0.0

        self.ask_x_1 = 0.0
        self.bid_x_1 = 0.0

        self.vps = webdriver.Chrome(executable_path=chrome_dir)

        self.web_access()
        sleep((datetime.datetime.now().replace(hour=9, minute=0,
                                               second=30) - datetime.datetime.now()).seconds)  # Hen gio chay run()
        print('=================================********* BAT DAU VAO PHIEN *********=================================')
        self.run()
        print('Tien hanh huy cac lenh chua khop.....')
        self.vps.find_element_by_xpath('//*[@id="orderPS"]/div[4]/button').click()  # Huy cac lenh LO chua khop
        print('Done!')
        print('=================================********* KET THUC PHIEN *********=================================')
        self.export_log()
        print('Xuat du lieu thanh cong !')

    # Ham dung de truy cap bang gia
    def web_access(self):

        # Dang nhap vao trang dat lenh
        self.vps.maximize_window()  # De max window
        self.vps.get("https://smartpro.vps.com.vn/")
        sleep(6)
        self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[2]/input').send_keys(self.acc_list[0])
        sleep(0.3)
        self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[3]/input').send_keys(self.acc_list[1])
        sleep(0.3)
        self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[6]/button[1]').click()
        sleep(6)
        self.vps.find_element_by_xpath('//*[@id="right_stock_cd"]/option[2]').click()  # F2M
        sleep(0.3)
        self.vps.find_element_by_id("right_order_type").click()  # Chon menu kieu lenh
        sleep(0.3)
        self.vps.find_element_by_xpath('//*[@id="select_type"]/span[2]').click()  # Chon lenh dieu kien
        sleep(0.3)
        self.vps.find_element_by_id("custom_select_order_type").click()  # Chon kieu lenh dieu kien
        sleep(0.3)
        self.vps.find_element_by_xpath('//*[@id="select_order_type"]/span[4]').click()  # Chon arbitrage
        #sleep(0.3)
        #self.vps.find_element_by_xpath('//*[@id="ab_code"]/option[1]').click()  # Chon ma HD thu 1 de arb (F1M)
        sleep(1)
        self.vps.find_element_by_xpath('/html/body/div[1]/aside/ul/li[2]/a').click()  # Bam vao nut cai dat
        sleep(1)
        self.vps.find_element_by_xpath('//*[@id="config_setting"]/div[1]/label[2]/span').click()  # Tat xac nhan lenh
        sleep(0.3)
        self.vps.find_element_by_xpath(
            '//*[@id="config_setting"]/div[2]/label[2]/span').click()  # Tat thong bao dat lenh
        sleep(0.3)
        self.vps.find_element_by_xpath(
            '//*[@id="config_setting"]/div[3]/label[2]/span').click()  # Tat thong bao khop lenh
        sleep(0.3)
        self.vps.find_element_by_xpath(
            '//*[@id="config_setting"]/div[4]/label[2]/span').click()  # Tat thong bao huy lenh
        sleep(0.3)
        self.vps.find_element_by_id('btnSaveConfig').click()  # Bam vao save
        sleep(6)
        self.vps.find_element_by_xpath('/html/body/div[1]/aside/ul/li[1]/a').click()  # Bam lai vao nut giao dich
        sleep(3)
        self.vps.find_element_by_xpath('//*[@id="right_btnordertype"]/div/span[3]').click() #Chon MTL
        sleep(3)
        self.vps.find_element_by_xpath('//*[@id="mainFooter"]/div[2]/a[1]').click()  # Chon danh sach lenh
        sleep(3)
        self.vps.find_element_by_xpath(
            '//*[@id="footerPanel"]/div[1]/span[2]/label[2]/input').click()  # Chon bang cho khop

    # Ham dung de login lai
    def re_login(self):
        try:
            self.vps.find_element_by_xpath(
                "//button[contains(text(),'OK')]").click()  # click ok de thoat ra man hinh login
            sleep(3)
            self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[2]/input').send_keys(self.acc_list[0])
            sleep(0.2)
            self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[3]/input').send_keys(self.acc_list[1])
            sleep(0.2)
            self.vps.find_element_by_xpath('//*[@id="form-login"]/div[2]/div[6]/button[1]').click()
            sleep(6)
            self.vps.find_element_by_xpath('//*[@id="right_stock_cd"]/option[2]').click()  # F2M
            sleep(0.2)
            self.vps.find_element_by_xpath('//*[@id="orderPS"]/form/div[6]/div[4]/label[2]/span').click()  # Swich to On
            sleep(0.2)
            self.vps.find_element_by_xpath('//*[@id="ab_code"]/option[1]').click()  # Chon ma HD thu 1 de arb (F1M)
            sleep(0.2)
            self.vps.find_element_by_xpath('//*[@id="right_btnordertype"]/div/span[3]').click() #Chon MTL
            self.vps.find_element_by_xpath('//*[@id="mainFooter"]/div[2]/a[1]').click()  # Chon danh sach lenh
            sleep(3)
            self.vps.find_element_by_xpath(
                '//*[@id="footerPanel"]/div[1]/span[2]/label[2]/input').click()  # Chon bang cho khop
        except:
            pass

    def run(self):
        try:
            while datetime.datetime.now().time() < datetime.time(hour=14, minute=29, second=30):
                # Get data
                self.time_now = datetime.datetime.now()
                now_second = self.time_now.second

                try:
                    data = requests.get(
                        'https://plus24.mbs.com.vn/PriceboardCore/api/data/snapshot?type=stockinfor&keys=VN30F2110,VN30F2111,VN30F2112,VN30F2203,GB05F2112,GB05F2203,GB05F2206,GB10F2112,GB10F2203,GB10F2206,').json()
                    self.bid_x = float(data['d'][0]['msg'].split(";")[5])
                    self.bid_x_1 = float(data['d'][0]['msg'].split(";")[3])
                    self.ask_x = float(data['d'][0]['msg'].split(";")[11])
                    self.ask_x_1 = float(data['d'][0]['msg'].split(";")[13])
                    self.bid_y = float(data['d'][1]['msg'].split(";")[5])
                    self.bid_y_1 = float(data['d'][1]['msg'].split(";")[3])
                    self.ask_y = float(data['d'][1]['msg'].split(";")[11])
                    self.ask_y_1 = float(data['d'][1]['msg'].split(";")[13])

                except:
                    continue

                if now_second >= self.last_time_second or datetime.time(hour=11,
                                                                        minute=30) <= self.time_now.time() <= datetime.time(
                    hour=13, minute=0):
                    self.diff[0][-1] = self.ask_x - self.bid_y
                    self.diff[1][-1] = self.ask_y - self.bid_x
                else:
                    self.diff[0].append(self.ask_x - self.bid_y)
                    self.diff[1].append(self.ask_y - self.bid_x)
                self.last_time_second = now_second

                # Calculate SMA
                self.MA[0] = sum(self.diff[0][-self.MA_priod:]) / min(self.MA_priod, len(self.diff[0]))
                self.MA[1] = sum(self.diff[1][-self.MA_priod:]) / min(self.MA_priod, len(self.diff[1]))

                # ===========================================GIAO DICH==========================================#
                for i in range(len(self.over_tp)):
                    if abs(self.diff[0][-1]) < 15 and abs(
                            self.diff[1][-1]) < 10:  # Gioi han spread side 0 < 15, side 1 < 10
                        tp = min(self.ask_y - self.bid_y,
                                 self.profit)  # Cai takeprofit o moc nho hon gia spread va tp tham so

                        # ------------------------------------------DAT LENH-------------------------------------------#
                        # Side 0:
                        if self.bid_x - self.bid_y - self.MA[0] - tp - self.fee + self.over_tp[i] - 0.1 > 0 and \
                                self.position[0][i] == 0 and self.time_now.time() < datetime.time(hour=14, minute=20):
                            try:
                                # Dat lenh LO
                                lp0 = round(self.bid_y + 0.1, 1)  # Gia lenh LO side 0 se dat
                                self.vps.find_element_by_id('right_price').clear()
                                self.vps.find_element_by_id('right_price').send_keys(Keys.BACKSPACE)
                                self.vps.find_element_by_id('right_price').send_keys(str(lp0))
                                sleep(0.2)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="orderPS"]/div[2]/button').click()  # Mo lenh Long F2
                                sleep(2)
                                # Kiem tra lenh dat va luu cac ID lenh
                                id = self.vps.find_element_by_xpath(
                                    '/html/body/footer[1]/div[4]/table/tbody/tr[1]/td[11]').get_attribute(
                                    'id')  # Xac dinh id trang thai dong dau tien
                                if id != '':
                                    if self.id_list.count(id) == 0:
                                        st = self.vps.find_element_by_id(id).text  # Lay trang thai cua lenh
                                        if st == 'Chờ khớp':
                                            self.position[0][i] = -1
                                            self.target[0][i] = self.MA[0] - self.over_tp[i]
                                            self.id_list.append(id)
                                            self.id_cancel[0][i] = 'btne_' + id[3:]
                                            self.order_price[0][i] = lp0
                                            print('{}: Dat lenh LO side 0: Short {}: {} and Long {}: {}, id: {} type:{}'
                                                  .format(self.time_now.time(), self.symbol_list[0],
                                                          self.bid_x, self.symbol_list[1], lp0, self.id_cancel[0][i],
                                                          i))
                                            self.vps.find_element_by_xpath(
                                                '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang

                                        elif st == 'Đã khớp':
                                            self.position[0][i] = 1
                                            self.target[0][i] = self.MA[0] - self.over_tp[i]
                                            print('{}: Open trade side 0: Short {}: {} and Long {}: {}, type:{}'
                                                  .format(self.time_now.time(), self.symbol_list[0],
                                                          self.bid_x, self.symbol_list[1], lp0, i))
                                            self.vps.find_element_by_xpath(
                                                '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang

                                        else:
                                            print(
                                                'CANH BAO: Loi dat lenh LO side 0: Short {}: {} and Long {}: {}, type:{} - Loi trang thai'
                                                    .format(self.symbol_list[0], self.bid_x, self.symbol_list[1], lp0,
                                                            i))
                                    else:
                                        print(
                                            'CANH BAO: Loi dat lenh LO side 0: Short {}: {} and Long {}: {}, type:{} - Trung ID cu'
                                                .format(self.symbol_list[0], self.bid_x, self.symbol_list[1], lp0, i))
                                else:
                                    print(
                                        'CANH BAO: Loi dat lenh LO side 0: Short {}: {} and Long {}: {}, type:{} - ID rong'
                                            .format(self.symbol_list[0], self.bid_x, self.symbol_list[1], lp0, i))
                            except:
                                print('CANH BAO: Dat lenh LO Short {} and Long {}, type:{} khong thanh cong!!!'
                                      .format(self.symbol_list[0], self.symbol_list[1], i))
                                print('Tien hanh dang nhap lai...')
                                self.re_login()
                                print('Dang nhap lai hoan tat !!!')

                        # Side 1:
                        elif self.ask_y - self.ask_x - self.MA[1] - self.fee - tp + self.over_tp[i] - 0.1 > 0 and \
                                self.position[1][i] == 0 and self.time_now.time() < datetime.time(hour=14, minute=20):
                            try:
                                # Dat lenh LO
                                lp1 = round(self.ask_y - 0.1, 1)  # Gia lenh LO side 1 se dat
                                self.vps.find_element_by_id('right_price').clear()
                                self.vps.find_element_by_id('right_price').send_keys(Keys.BACKSPACE)
                                self.vps.find_element_by_id('right_price').send_keys(str(lp1))
                                sleep(0.2)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="orderPS"]/div[1]/button').click()  # Mo lenh Short F2
                                sleep(2)
                                # Kiem tra lenh dat va luu cac ID lenh
                                id = self.vps.find_element_by_xpath(
                                    '/html/body/footer[1]/div[4]/table/tbody/tr[1]/td[11]').get_attribute(
                                    'id')  # Xac dinh id trang thai dong dau tien
                                if id != '':
                                    if self.id_list.count(id) == 0:
                                        st = self.vps.find_element_by_id(id).text  # Lay trang thai cua lenh
                                        if st == 'Chờ khớp':
                                            self.position[1][i] = -1
                                            self.target[1][i] = self.MA[1] - self.over_tp[i]
                                            self.id_list.append(id)
                                            self.id_cancel[1][i] = 'btne_' + id[3:]
                                            self.order_price[1][i] = lp1
                                            print('{}: Dat lenh LO side 1: Long {}: {} and Short {}: {}, id: {} type:{}'
                                                  .format(self.time_now.time(), self.symbol_list[0],
                                                          self.ask_x, self.symbol_list[1], lp1, self.id_cancel[1][i],
                                                          i))
                                            self.vps.find_element_by_xpath(
                                                '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang

                                        elif st == 'Đã khớp':
                                            self.position[1][i] = 1
                                            self.target[1][i] = self.MA[1] - self.over_tp[i]
                                            print('{}: Open trade side 1: Long {}: {} and Short {}: {}, type:{}'
                                                  .format(self.time_now.time(), self.symbol_list[0],
                                                          self.ask_x, self.symbol_list[1], lp1, i))
                                            self.vps.find_element_by_xpath(
                                                '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang

                                        else:
                                            print(
                                                'CANH BAO: Loi dat lenh LO side 1: Long {}: {} and Short {}: {}, type:{} - Loi trang thai'
                                                    .format(self.symbol_list[0], self.ask_x, self.symbol_list[1], lp1,
                                                            i))
                                    else:
                                        print(
                                            'CANH BAO: Loi dat lenh LO side 1: Long {}: {} and Short {}: {}, type:{} - Trung ID cu'
                                                .format(self.symbol_list[0], self.ask_x, self.symbol_list[1], lp1, i))
                                else:
                                    print(
                                        'CANH BAO: Loi dat lenh LO side 1: Long {}: {} and Short {}: {}, type:{} - ID rong'
                                            .format(self.symbol_list[0], self.ask_x, self.symbol_list[1], lp1, i))
                            except:
                                print('CANH BAO: Mo lenh Long {} and Short {}, type:{} khong thanh cong!!!'
                                      .format(self.symbol_list[0], self.symbol_list[1], i))
                                print('Tien hanh dang nhap lai...')
                                self.re_login()
                                print('Dang nhap lai hoan tat !!!')

                        # ------------------------------------------HUY LENH/CHECK KHOP-------------------------------------------#
                        # Side 0:
                        elif self.position[0][i] == -1 and (
                                self.bid_x_1 - self.bid_y - self.MA[0] - tp - self.fee + self.over_tp[
                            i] + self.zone_len <= 0
                                or self.bid_y > self.order_price[0][i]):
                            try:
                                self.vps.find_element_by_id(self.id_cancel[0][i]).click()
                                sleep(1)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang
                                sleep(0.5)
                                try:
                                    self.vps.find_element_by_id(self.id_cancel[0][i]).click()
                                except:
                                    self.position[0][i] = 0
                                    print('{}: Huy lenh side 0, id: {} thanh cong'.format(self.time_now.time(),
                                                                                          self.id_cancel[0][i]))
                            except:
                                self.position[0][i] = 1
                                print('{}: Lenh side 0, id: {} da khop'.format(self.time_now.time(),
                                                                               self.id_cancel[0][i]))

                        # Side 1:
                        elif self.position[1][i] == -1 and (
                                self.ask_y - self.ask_x_1 - self.MA[1] - self.fee - tp + self.over_tp[
                            i] + self.zone_len <= 0
                                or self.ask_y < self.order_price[1][i]):
                            try:
                                self.vps.find_element_by_id(self.id_cancel[1][i]).click()
                                sleep(1)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="footerPanel"]/div[1]/span[3]/a[2]').click()  # Reload bang
                                sleep(0.5)
                                try:
                                    self.vps.find_element_by_id(self.id_cancel[1][i]).click()
                                except:
                                    self.position[1][i] = 0
                                    print('{}: Huy lenh side 1, id: {} thanh cong'.format(self.time_now.time(),
                                                                                          self.id_cancel[1][i]))
                            except:
                                self.position[1][i] = 1
                                print('{}: Lenh side 1, id: {} da khop'.format(self.time_now.time(),
                                                                               self.id_cancel[1][i]))


                        # ------------------------------------------DONG LENH-------------------------------------------#
                        # Side 0:
                        elif self.position[0][i] == 1 and self.diff[0][-1] < self.target[0][i] and abs(
                                self.bid_y - self.bid_y_1) < tp:
                            try:
                                self.vps.find_element_by_xpath('//*[@id="right_btnordertype"]/div/span[3]').click() #Chon MTL
                                sleep(0.1)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="orderPS"]/div[1]/button').click()  # Dong lenh Short F2
                                self.position[0][i] = 0
                                print('{}: Close trade side 0: Long {}: {} and Short {}: {}, type:{}, id: {}'
                                      .format(self.time_now.time(), self.symbol_list[0], self.ask_x,
                                              self.symbol_list[1], self.bid_y, i, self.id_cancel[0][i]))
                            except:
                                print(
                                    'CANH BAO: Dong lenh side 0: Long {} and Short {}, type:{}, id: {} khong thanh cong!!!'
                                        .format(self.symbol_list[0], self.symbol_list[1], i, self.id_cancel[0][i]))
                                print('Tien hanh dang nhap lai...')
                                self.re_login()
                                print('Dang nhap lai hoan tat !!!')

                        # Side 1:
                        elif self.position[1][i] == 1 and self.diff[1][-1] < self.target[1][i] and abs(
                                self.ask_y_1 - self.ask_y) < tp:
                            try:
                                self.vps.find_element_by_xpath('//*[@id="right_btnordertype"]/div/span[3]').click() #Chon MTL
                                sleep(0.1)
                                self.vps.find_element_by_xpath(
                                    '//*[@id="orderPS"]/div[2]/button').click()  # Dong lenh Long F2
                                self.position[1][i] = 0
                                print('{}: Close trade side 1: Short {}: {} and Long {}: {}, type:{}, id: {}'
                                      .format(self.time_now.time(), self.symbol_list[0], self.bid_x,
                                              self.symbol_list[1], self.ask_y, i, self.id_cancel[1][i]))
                            except:
                                print(
                                    'CANH BAO: Dong lenh side 1: Short {} and Long {}, type:{}, id: {} khong thanh cong!!!'
                                        .format(self.symbol_list[0], self.symbol_list[1], i, self.id_cancel[1][i]))
                                print('Tien hanh dang nhap lai...')
                                self.re_login()
                                print('Dang nhap lai hoan tat !!!')
                    else:
                        pass
        except KeyboardInterrupt:
            # Ghi file log tam thoi
            f = open("D:/temp_log.txt", "a")
            f.write(str([self.diff[0][-self.MA_priod - 2:], self.diff[1][-self.MA_priod - 2:]]))
            f.write('\n' + str(self.position))
            f.write('\n' + str(self.target))
            f.write('\n' + str(self.id_list))
            f.close()
            print('Xuat temp_log.txt thanh cong!!!')

    def export_log(self):
        f = open("D:/daily_log.txt", "a")
        f.write('\n\n===================================================\n')
        f.write(datetime.datetime.now().strftime("%d/%m/%Y"))
        f.write('\ndiff = ' + str([self.diff[0][-self.MA_priod - 2:], self.diff[1][-self.MA_priod - 2:]]))
        f.write('\nposition = ' + str(self.position))
        f.write('\ntarget = ' + str(self.target))
        f.write('\nid list = ' + str(self.id_list))
        f.close()


if __name__ == "__main__":
    symbol_list = ['VN30F1M', 'VN30F2M']
    chrome_dir = "D:/chromedriver_win32/chromedriver.exe"
    profit = 1
    fee = 1
    MA_priod = 30
    over_tp = [1.5, 1, 0.5]
    acc_list = ['421316', 'Manhtien@194']
    import_log = 0
    zone_len = 0.3

    trading = Trading(symbol_list, chrome_dir, profit, fee, MA_priod, over_tp, acc_list, import_log, zone_len)
