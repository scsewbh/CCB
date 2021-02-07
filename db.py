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

def verify_watch(PID, author):
    mycursor = mydb.cursor()
    sql = "SELECT PID_1, PID_2, PID_3, PID_4, PID_5 from members where Username = '%s'" % (author)
    # msql = "SELECT * FROM members"
    # qsql = "INSERT IGNORE INTO members (Username, PID_1, PID_2, PID_3, PID_4, PID_5) VALUES (%s, %s, %s, %s, %s, %s)"
    # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
    mycursor.execute(sql)
    PIDs = mycursor.fetchall()
    if PID in PIDs[0]:
        return 1  # One for PID already in your personal monitor
    elif PIDs[0] == 'None' or PIDs[1] == 'None' or PIDs[2] == 'None' or PIDs[3] == 'None' or PIDs[4] == 'None':
        return 2  # Good to Go
    else:
        return 3  # Full or Error

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
        sql = "INSERT IGNORE INTO products (ProductName, Link) VALUES (%s, %s)"
        #Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
        mycursor.executemany(sql, self.data)
        mydb.commit()
        print(mycursor.rowcount, "was inserted to table.")

    def results(self, listUrl):
        self.data = []
        self.browser.get(listUrl)
        listData = self.browser.page_source
        soup = bs(listData, 'html.parser')
        a = soup.find_all('a', class_='a-link-normal a-text-normal')

        for parLink in a:
            pHref = parLink['href'].split('?_encoding=')[0]
            if '/ref=' in pHref:
                pHref = pHref.split('/ref=')[0]
            pHref = pHref.split('/dp/')[1]
            self.data.append((pHref, amzn_basep_url + pHref))
        self.passToDatabase()

    def page_with_list(self, page_urls):
        #Takes the array of pages that are list eg: bestsellers, new releases
        for url in page_urls:
            self.results(url)

    #------------------------------PARSING----------------------------------------
    def passToParser(self):
        mycursor = mydb.cursor()
        mycursor.execute("SELECT Link FROM products") #LIMIT AT 3 FOR TESTING - PARTITION OUT FOR HEROKU SOMEHOW
        myresult = mycursor.fetchall()
        for url in myresult:
            print(url[0])
            self.page_parser(url[0])
        self.browser.quit()

    def page_parser(self, url):
        self.browser.get(url)
        self.page_data = {}
        try:
            elem = self.browser.find_element_by_css_selector('#ppd')
        except selenium.common.exceptions.NoSuchElementException:
            try:
                elem = self.browser.find_element_by_css_selector('#dp-container')
            except selenium.common.exceptions.NoSuchElementException:
                return

        try:
            image = elem.find_element_by_id('leftCol')
            content = image.find_element_by_class_name('imgTagWrapper')
            con = content.find_element_by_tag_name('img')
            img_src = con.get_attribute('data-old-hires')
        except selenium.common.exceptions.NoSuchElementException:
            return

        main = elem.find_element_by_id('centerCol').text
        splitted = main.splitlines()
        product_name = elem.find_element_by_id('productTitle').text
        print(product_name)
        self.page_data['name'] = product_name
        temp = 0
        for line in splitted:
            if 'Price: $' in line:
                temp += 1
                if temp == 1:
                    self.page_data['price'] = (line.split('$')[1]).split(' ')[0]
                if temp == 2:
                    self.page_data['discounted_price'] = (line.split('$')[1]).split(' ')[0]
            if 'Was: $' in line:
                temp += 1
                self.page_data['price'] = (line.split('$')[1]).split(' ')[0]
            if 'With Deal: $' in line:
                self.page_data['discounted_price'] = (line.split('$')[1]).split(' ')[0]
            if 'price' not in self.page_data:
                self.page_data['price'] = 'Not Listed'
        self.page_data['img_url'] = img_src
        self.page_data['product_id'] = url.replace(amzn_basep_url, '')
        self.dataOrganizer()
        self.passProductsToDBs()

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
            sql = "INSERT IGNORE INTO item_data (Name, Price, Img_URL, PID) VALUES (%s, %s, %s, %s)"  # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
            mycursor.execute(sql, self.item_dataHolder)
            mydb.commit()

            #---------------------------------------------------------

            mycursor = mydb.cursor()
            sql = "INSERT IGNORE INTO sync_data (PID, Price) VALUES (%s, %s)"  # Insert Ignore allows me to insert products and skip over the duplicates and the error it gives.
            mycursor.execute(sql, self.sync_dataHolder)
            mydb.commit()


verify_watch('dfgdfg', 'Happy#e4564')
