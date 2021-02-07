from bs4 import BeautifulSoup as bs
import mysql.connector
from selenium import webdriver
import selenium.common.exceptions
import os

#-----------------------Settings--------------------------

chrome_options = webdriver.ChromeOptions()

mydb = mysql.connector.connect(
    host="34.86.36.213",
    user="root",
    password="Heroku3031*SPN",
    database="discord"
)

amzn_basep_url = 'https://www.amazon.com/dp/'

#CREATE TABLE products (PID VARCHAR(20) PRIMARY KEY, Link TEXT);
#CREATE TABLE item_data (PID VARCHAR(20), Name TEXT, Price DECIMAL(5,2), Img_URL TEXT, PRIMARY KEY (PID), FOREIGN KEY (PID) REFERENCES products(PID));
#CREATE TABLE sync_data (ProductName VARCHAR(255), Price DECIMAL(5,2), PRIMARY KEY (ProductName), FOREIGN KEY (ProductName) REFERENCES products(ProductName));
#CREATE TABLE members (USER_ID VARCHAR(30), PID_1 VARCHAR(20), PID_2 VARCHAR(20), PID_3 VARCHAR(20), PID_4 VARCHAR(20), PID_5 VARCHAR(20), PRIMARY KEY (USER_ID));

class AMZN:
    def __init__(self):
        self.browser = webdriver.Chrome(executable_path='C:\\Users\\scsew\\Desktop\\chromedriver.exe', chrome_options=chrome_options)
        self.data = []
        self.page_data = {}
        self.item_dataHolder = ()
        self.sync_dataHolder = ()
        self.item_data_names = ['name', 'price', 'img_url', 'product_id']
        self.sync_data_names = ['product_id', 'discounted_price']

    #--------------------------------ADDING TO DB---------------------------------
    def passToDatabase(self):
        mycursor = mydb.cursor()
        sql = "INSERT IGNORE INTO products (PID, Link) VALUES (%s, %s)"
        #Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
        mycursor.executemany(sql, self.data)
        mydb.commit()
        print(mycursor.rowcount, "was inserted to table.")

    #------------------------------PARSING----------------------------------------
    def page_parser(self, PID):
        url = amzn_basep_url + PID
        self.data = [(PID, url)]
        try:
            self.browser.get(url)
        except selenium.common.exceptions:
            return None
        self.page_data = {}
        try:
            elem = self.browser.find_element_by_css_selector('#ppd')
        except selenium.common.exceptions.NoSuchElementException:
            try:
                elem = self.browser.find_element_by_css_selector('#dp-container')
            except selenium.common.exceptions.NoSuchElementException:
                return None

        try:
            image = elem.find_element_by_id('leftCol')
            content = image.find_element_by_class_name('imgTagWrapper')
            con = content.find_element_by_tag_name('img')
            img_src = con.get_attribute('data-old-hires')
        except selenium.common.exceptions.NoSuchElementException:
            img_src = 'https://vcunited.club/wp-content/uploads/2020/01/No-image-available-2.jpg'

        main = elem.find_element_by_id('centerCol').text
        splitted = main.splitlines()
        product_name = elem.find_element_by_id('productTitle').text
        print(product_name)
        self.page_data['product_id'] = PID
        self.page_data['name'] = product_name
        temp = 0
        for line in splitted:
            if 'Price: $' in line:
                temp += 1
                if temp == 1:
                    self.page_data['price'] = (line.split('$')[1]).split(' ')[0]
                if temp == 2:
                    self.page_data['price'] = (line.split('$')[1]).split(' ')[0]
                    self.page_data['discounted_price'] = (line.split('$')[1]).split(' ')[0]
            if 'Was: $' in line:
                temp += 1
            if 'With Deal: $' in line:
                self.page_data['price'] = (line.split('$')[1]).split(' ')[0]
                self.page_data['discounted_price'] = (line.split('$')[1]).split(' ')[0]
            if 'price' not in self.page_data:
                self.page_data['price'] = 'Not Listed'
        self.page_data['img_url'] = img_src
        self.passToDatabase()
        self.dataOrganizer()
        self.passProductsToDBs()
        if self.page_data['price'] == 'Not Listed':
            return -1
        else:
            return self.page_data['price']

    #INITIAL PASS SETUP
    def dataOrganizer(self):
        self.item_dataHolder = ()
        self.sync_dataHolder = ()
        for value in self.item_data_names:
            if value in self.page_data:
                self.item_dataHolder += (self.page_data[value],)
            else:
                self.item_dataHolder += (None,)

        for value in self.sync_data_names:
            if value in self.page_data:
                self.sync_dataHolder += (self.page_data[value],)
            elif value == 'discounted_price':
                self.sync_dataHolder += (self.page_data['price'],)
            else:
                self.sync_dataHolder += (None,)

    def passProductsToDBs(self):
        # item_data (Name TEXT, Price DECIMAL(5,2), Img_URL TEXT, ProductName VARCHAR(255), PRIMARY KEY (ProductName), FOREIGN KEY (ProductName) REFERENCES products(ProductName))")
        # sync_data (ProductName VARCHAR(255), Price DECIMAL(5,2), Savings TINYINT, PRIMARY KEY (ProductName), FOREIGN KEY (ProductName) REFERENCES products(ProductName))")
        if self.page_data['price'] != 'Not Listed':
            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO item_data (PID, Name, Price, Img_URL) VALUES (%s, %s, %s, %s)"  # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
            mycursor.execute(sql, self.item_dataHolder)
            mydb.commit()

            #---------------------------------------------------------

            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO sync_data (PID, Price) VALUES (%s, %s)"  # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
            mycursor.execute(sql, self.sync_dataHolder)
            mydb.commit()

