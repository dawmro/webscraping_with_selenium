from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import sqlite3



def save_pse_data_to_db(my_dict):
    try:
        pse = "pse"
        conn = sqlite3.connect("db/pse_data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS """+pse+"""(
            timeNow, 
            zapotrzebowanie_mw, 
            generacja_mw, 
            el_cieplne,
            el_wodne,
            el_wiatrowe,
            el_fotowoltaiczne,
            el_inne,
            saldo_wymiany,
            czestotliwosc
            )""")
            
        c.execute("""INSERT INTO """+pse+""" VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",(
            my_dict.get('timeNow'),
            my_dict.get('zapotrzebowanie_mw'),
            my_dict.get('generacja_mw'),
            my_dict.get('el_cieplne'),
            my_dict.get('el_wodne'),
            my_dict.get('el_wiatrowe'),
            my_dict.get('el_fotowoltaiczne'),
            my_dict.get('el_inne'),
            my_dict.get('saldo_wymiany'),
            my_dict.get('czestotliwosc')))
            
        conn.commit()  
        c.close()
        conn.close()
        return "True"
    except:
        return "False"
        
        
        
def get_page_content(url):

    options = Options()
    options.add_argument("--headless") # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox') # Bypass OS security model
    options.add_argument('--disable-gpu')  # applicable to windows os only
    options.add_argument('start-maximized') # 
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    
    browser = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    page = browser.get(url)
    time.sleep(3)
    content = browser.page_source
    browser.quit()
    
    return content
          



def get_pse_data(content):

    my_dict = {}
    my_dict['timeNow'] = str(int(time.time()))
    
    soup = BeautifulSoup(content, "html.parser")
    tab = soup.find("table",{"class":"legend-table-subsite"})

    zapotrzebowanie_mw = tab.find("td",{"id":"zapotrzebowanie-mw"}).text.replace(" ", "")
    my_dict['zapotrzebowanie_mw'] = int(zapotrzebowanie_mw)
    
    generacja_mw = tab.find("td",{"id":"generacja-mw"}).text.replace(" ", "")
    my_dict['generacja_mw'] = int(generacja_mw)
    
    el_cieplne = tab.find("td",{"id":"el-cieplne"}).text.replace(" ", "")
    my_dict['el_cieplne'] = int(el_cieplne)
    
    el_wodne = tab.find("td",{"id":"el-wodne"}).text.replace(" ", "")
    my_dict['el_wodne'] = int(el_wodne)

    el_wiatrowe = tab.find("td",{"id":"el-wiatrowe"}).text.replace(" ", "")
    my_dict['el_wiatrowe'] = int(el_wiatrowe)
    
    el_fotowoltaiczne = tab.find("td",{"id":"el-fotowoltaiczne"}).text.replace(" ", "")
    my_dict['el_fotowoltaiczne'] = int(el_fotowoltaiczne)
    
    el_inne = tab.find("td",{"id":"el-inne"}).text.replace(" ", "")
    my_dict['el_inne'] = int(el_inne)
    
    saldo_wymiany = tab.find("td",{"id":"saldo-wymiany"}).text.replace(" ", "")
    if "IMPORT" in saldo_wymiany:  
        saldo_wymiany = saldo_wymiany.replace("IMPORT", "")
        saldo_wymiany = int(saldo_wymiany)*(-1)
    else:
        saldo_wymiany = saldo_wymiany.replace("EKSPORT", "")
    my_dict['saldo_wymiany'] = int(saldo_wymiany)
    
    czestotliwosc = tab.find("td",{"id":"czestotliwosc"}).text.replace(" ", "").replace(",", ".")
    my_dict['czestotliwosc'] = float(czestotliwosc)
    
    return my_dict


def main():

    url = f"https://www.pse.pl/dane-systemowe"


    while True:
        
        my_dict = {}
        try:
            print("\nStarting getting data")
            content = get_page_content(url)
            my_dict = get_pse_data(content)
        except:
            print("getting data failed")
        
        if len(my_dict) > 0:    
            print(f"Add to db success?: {save_pse_data_to_db(my_dict)}")
            
        print("Waiting 60 seconds")
        time.sleep(60)

   
if __name__ == '__main__':
    main()

