import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
def init_database():
        connection = sqlite3.connect('movies.db')
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kdrama(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_title text,
        date text,
        description text,
        link text,
        image_lnk text,
        downloads text
                                                                         
)""")
        connection.commit()
        connection.close()

def data_exists(title, date):
    connection = sqlite3.connect('movies.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM kdrama WHERE movie_title=? AND date=?", (title, date))
    count = cursor.fetchone()[0]
    connection.close()
    return count > 0

def add_data(title, date, description, link,img, download_lnk):
    if not data_exists(title, date):
        connection = sqlite3.connect('movies.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO kdrama (movie_title, date, description, link ,image_lnk, downloads) VALUES (?, ?, ?, ?, ?, ?)", (title, date, str(description), link, img,  download_lnk))
        connection.commit()
        connection.close()

base_url = 'https://nkiri.com/category/asian-movies/download-korean-movies/'
n = range(1,8)
for num in n:
    url = f'{base_url}page/{num}'
    print(f"Getting data for page {num}")
    if num == 7:
        print("Successfully added into Database!")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for text in soup.find_all('article'):
        title = text.find('h2', {'class': 'blog-entry-title entry-title'})
        f_title = title.text.strip()
        date = text.find('div', {'class': 'blog-entry-date clr'})
        f_date = date.text.strip()
        link = title.find('a')['href']
        img = text.find('img')
        if img:
            image = img.get('src')
        re_response = requests.get(link)
        re_soup = BeautifulSoup(re_response.text, 'html.parser')
        for shit in re_soup.find_all('a', {'class': 'elementor-button elementor-button-link elementor-size-md'}):
            download = shit.get('href')
            if 'html' in download:
                downloadlnk = download

                
        for item in re_soup.find_all('div', {'class': 'overview'}):
            desc = item.find('p')
            desc_text = desc.text.strip()

           
                    
                
            init_database()
            add_data(f_title, f_date, desc_text, link, image, downloadlnk)


# options = Options()
# options.add_argument("--headless")
# driver = webdriver.Chrome(options=options)
# driver.get(downloadlnk)
# dbtn = driver.find_element(By.ID, 'downloadbtn')
# dbtn.send_keys(Keys.ENTER)
