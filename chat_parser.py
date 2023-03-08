import json
import os
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

import csv

#csv 編輯器
class CsvEditor():
    def __init__(self, filename:str, field_list:list) -> None:
        #設定csv寫入器
        self.csvfile = open(filename, 'w', newline='', encoding='utf8')
        self.csvwriter = csv.writer(self.csvfile)
        #寫入欄位資料
        self.csvwriter.writerow(field_list)
    
    #關閉檔案
    def close(self) -> None:
        self.csvfile.close()
    
    #寫入表格
    def writerows(self, table):
        if len(table):
            self.csvwriter.writerows(table)

class Statistics():
    def __init__(self, tagname) -> None:
        self.id_list = []
        self.table = []
        self.tagname = tagname
        self.elements = []
        self.is_reapeat_stat = False
    
    #找聊天室所有相同的訊息物件
    def find_elements(self, browser:webdriver.Chrome):
        elements = browser.find_elements(By.TAG_NAME, self.tagname)
        #順序顛倒 因為 隨時間增加最早出現的訊息會消失
        self.elements = elements[::-1]
    
    #檢查是否統計過
    def check_reapeat_stat(self):
        try:
            id = self.elements[0].get_attribute('id')
            if len(self.elements) == 0 or id in self.id_list:
                self.is_reapeat_stat = True
            else:
                self.is_reapeat_stat = False
        except selenium.common.exceptions.StaleElementReferenceException:
            print('53')
            self.is_reapeat_stat = True
        except IndexError:
            print('56')
            self.is_reapeat_stat = True

    #統計資料
    def stat(self):
        #檢查是否全部已統計
        self.check_reapeat_stat()
        if self.is_reapeat_stat:
            return
        
        #開始統計資料
        self.is_reapeat_stat = False
        table = []
        for e in self.elements:
            #從最新的訊息開始統計
            try:
                id = e.get_attribute('id')
            except selenium.common.exceptions.StaleElementReferenceException:
                print('74')
                break
            
            if id in self.id_list:
                #統計到重覆的 統計結束
                break

            #解析元素的資料
            try:
                table.append(self.get_stat_data(e))
            except selenium.common.exceptions.StaleElementReferenceException:
                print('85')
                pass
            self.id_list.append(id)
            
        #訊息從最舊的統整到table
        self.table.extend(table[::-1])

    #資料已寫入 重製表格
    def reset_table(self):
        self.table = []
    
class ChatStat(Statistics):
    def __init__(self) -> None:
        super().__init__('yt-live-chat-text-message-renderer')
    
    #解析元素的資料
    def get_stat_data(self, element) -> tuple:
        timestamp = element.find_element(By.ID, 'timestamp').get_attribute('innerHTML')
        name = element.find_element(By.ID, 'author-name').text
        msg = element.find_element(By.ID, 'message')

        if not msg.text:
            #判斷是不是表情符號
            html = msg.get_attribute('innerHTML')
            if 'emoji' in html:
                msg = 'emoji..'
        else:
            msg = msg.text
        #print('CHAT', 't =', timestamp, 'name =', name, 'msg =', msg)
        return (timestamp, name, msg)


class MemberStat(Statistics):
    def __init__(self) -> None:
        super().__init__('yt-live-chat-membership-item-renderer')
    
    #解析元素的資料
    def get_stat_data(self, element) -> tuple:
        timestamp = element.find_element(By.ID, 'timestamp').get_attribute('innerHTML')
        name = element.find_element(By.ID, 'author-name').text
        print('MBER', 't =', timestamp, 'name =', name)
        return (timestamp, name)

class SuperStat(Statistics):
    def __init__(self) -> None:
        super().__init__('yt-live-chat-paid-message-renderer')
        self.total_dict = {}

    #解析元素的資料
    def get_stat_data(self, element) -> tuple:
        timestamp = element.find_element(By.ID, 'timestamp').get_attribute('innerHTML')
        name = element.find_element(By.ID, 'author-name').text
        msg = element.find_element(By.ID, 'message')

        if not msg.text:
            #判斷是不是表情符號
            html = msg.get_attribute('innerHTML')
            if 'emoji' in html:
                msg = 'emoji..'
            else:
                msg = ''
        else:
            msg = msg.text
        
        purchase = element.find_element(By.ID, 'purchase-amount').text
        currency, amoumt = self.currency_split(purchase)
        self.count_total(currency, amoumt)
        print(self.total_dict)

        print('SCHT', 't = ', timestamp, 'cur = ', currency, 'amoumt = ', amoumt, 'name =', name, 'msg =', msg)
        return (timestamp, name, msg, currency, amoumt)
    
    #分割貨幣和金額
    def currency_split(self, purchase):
        currency = ''
        amoumt = 0
        for i, c in enumerate(purchase):
            if ord('0') <= ord(c) <= ord('9'):
                currency = purchase[:i].strip()
                amoumt_str = purchase[i:].replace(',', '')
                amoumt = float(amoumt_str)
                return (currency, amoumt)
    
    #統計總金額
    def count_total(self, currency, amoumt):
        if not currency in self.total_dict:
            self.total_dict[currency] = 0
        self.total_dict[currency] += amoumt
    
    #儲存統計
    def save_total(self):
        with open('sc_total.csv', 'w', newline='', encoding='utf8') as csvfile:
            total = []
            for currency, amoumt in self.total_dict.items():
                total.append([currency, amoumt])
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['貨幣種類', '總金額(未換匯)'])
            csvwriter.writerows(total)

def save_file(chat_text_csv, menber_csv, super_chat_csv, chat_stat, super_stat, member_stat):
    print('write data')
    chat_text_csv.writerows(chat_stat.table)
    chat_stat.reset_table()
    super_chat_csv.writerows(super_stat.table)
    super_stat.reset_table()
    menber_csv.writerows(member_stat.table)
    member_stat.reset_table()

if __name__ == '__main__':
    #取得yt網址id
    id = 'FQHJL5ueV64'

    #設定瀏覽器選項
    options = Options()
    browser = webdriver.Chrome('./chromedriver', chrome_options=options)
    browser.implicitly_wait(3)

    #開啟網頁
    url = "https://www.youtube.com/watch?v=" + str(id)
    browser.get(url)

    #打開csv編輯器
    chat_text_csv = CsvEditor('chat_text.csv', ['time', 'name', 'content'])
    menber_csv = CsvEditor('menber.csv', ['time', 'name'])
    super_chat_csv = CsvEditor('super_chat.csv', ['time', 'name', 'content', 'currency', 'amount'])

    #尋找播放按鍵並播放
    btn = browser.find_element(By.CLASS_NAME, 'ytp-play-button')
    btn.click()
    print('start to parser')

    #切換到 chatframe iframe
    browser.switch_to.frame('chatframe')

    #設定統計器
    chat_stat = ChatStat()
    super_stat = SuperStat()
    member_stat = MemberStat()


    try:
        while browser.current_url == url:
            chat_stat.find_elements(browser)
            member_stat.find_elements(browser)
            super_stat.find_elements(browser)

            chat_stat.stat()
            member_stat.stat()
            super_stat.stat()

            if chat_stat.is_reapeat_stat:
                save_file(chat_text_csv, menber_csv, super_chat_csv, chat_stat, super_stat, member_stat)
                time.sleep(2)

            print("===========================\n")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
    
    #存檔
    save_file(chat_text_csv, menber_csv, super_chat_csv, chat_stat, super_stat, member_stat)
    chat_text_csv.close()
    super_stat.save_total()
    super_chat_csv.close()
    menber_csv.close()
