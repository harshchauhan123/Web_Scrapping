import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def chrome(headless=False):
    # support to get response status and headers
    d = webdriver.DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}
    opt = webdriver.ChromeOptions()
    if headless:
        opt.add_argument("--headless")
    opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    opt.add_argument("--disable-popup-blocking")
    browser = webdriver.Chrome(executable_path=r'H:\Web_scrapping\chromedriver-win64\chromedriver.exe', options=opt,desired_capabilities=d)
    browser.implicitly_wait(10)
    return browser
## Pass True if you want to hide chrome browser
browser = chrome()
browser.get('https://www.linkedin.com/login')
browser.implicitly_wait(3)
#enter username and password here
file = open('config.txt')
lines = file.readlines()

username = lines[0]
password = lines[1]

print(username,password)


elementID = browser.find_element_by_id('username')
elementID.send_keys(username)

elementID = browser.find_element_by_id('password')
elementID.send_keys(password)

elementID.submit()

links=f'https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+AND+%22India%22&sca_esv=600053872&rlz=1C1CHMO_en-GBIN907IN907&sxsrf=ACQVn0-uv2p18jQOi_r_0YQaSCUWzTvH8g%3A1705751874892&ei=QrWrZdX6Nb7SjuMP_ZuiwAs&ved=0ahUKEwjVo8_09OuDAxU-qWMGHf2NCLgQ4dUDCBA&uact=5&oq=site%3Alinkedin.com%2Fin%2F+AND+%22India%22&gs_lp=Egxnd3Mtd2l6LXNlcnAiIXNpdGU6bGlua2VkaW4uY29tL2luLyBBTkQgIkluZGlhIkjEHVCODVixF3ABeACQAQCYAaYBoAGsBaoBAzAuNbgBA8gBAPgBAeIDBBgBIEGIBgE&sclient=gws-wiz-serp#ip=1'
info = []

browser.get(links)
browser.implicitly_wait(2)
linkedin_urls=[my_elem.get_attribute("href") for my_elem in WebDriverWait(browser, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='yuRUbf']/a[@href]")))]
# linkedin_urls=[my_elem.get_attribute("href") for my_elem in WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, "//p[@class='sc-eYdvao kvdWiq']/a"))).get_attribute('href')]

#print(WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//p[@class='sc-eYdvao kvdWiq']/a"))).get_attribute('href'))
# print(linkedin_urls)


for link in linkedin_urls:
    browser.get(link)
    browser.implicitly_wait(1)
    def scroll_down_page(speed=8):
        current_scroll_position, new_height= 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            browser.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = browser.execute_script("return document.body.scrollHeight")

    scroll_down_page(speed=8)

    src = browser.page_source
    soup = BeautifulSoup(src, 'lxml')

    # Get Name of the person
    try:
        name_div = soup.find('div', {'class': 'pv-text-details__left-panel mr5'})
        first_last_name = name_div.find('h1').get_text().strip()
    except:
        first_last_name = None
    
    # Get Talks about section info
    try:
        talksAbout_tag = name_div.find('div', {'class': 'text-body-small t-black--light break-words pt1'})
        talksAbout = talksAbout_tag.find('span').get_text().strip()
    except:
        talksAbout = None
    
    # Get Location of the Person
    try:
        location_tag = name_div.find('div', {'class': 'pb2'})
        location = location_tag.find('span').get_text().strip()
    except:
        location = None
    
    # Get Title of the Person
    try:
        title = name_div.find('div', {'class': 'text-body-medium break-words'}).get_text().strip()
    except:
        title = None
    
    # Get Company Link of the Person
    try:
        exp_section = soup.find('section', {'id':'experience-section'})
        exp_section = exp_section.find('ul')
        li_tags = exp_section.find('div')
        a_tags = li_tags.find('a')

        company_link = a_tags['href']
        company_link = 'https://www.linkedin.com/' + company_link
    except:
        company_link = None

    # Get Job Title of the Person
    try:
        job_title = li_tags.find('h3', {'class': 't-16 t-black t-bold'}).get_text().strip()
    except:
        job_title = None
    
    # Get Company Name of the Person
    try:
        company_name = li_tags.find('p', {'class': 'pv-entity__secondary-title t-14 t-black t-normal'}).get_text().strip()
    except:
        company_name = None

    contact_page = link + 'detail/contact-info/'
    browser.get(contact_page)
    browser.implicitly_wait(1)

    contact_card = browser.page_source
    contact_page = BeautifulSoup(contact_card, 'lxml')
    # Get Linkdin Profile Link and Contact details of the Person
    try:
        contact_details = contact_page.find('section', {'class': 'pv-profile-section pv-contact-info artdeco-container-card ember-view'})
        contacts = []
        for a in contact_details.find_all('a', href=True):
            contacts.append(a['href'])
    except:
        contacts.append('')
    info.append([first_last_name, title, company_link, job_title, company_name, talksAbout, location, contacts])
    time.sleep(5)


column_names = ["Full Name", "Title", "Company URl", 'Job Title', 
                'Company Name', 'Talks About', 'Location', 'Profile Link and Contact']
df = pd.DataFrame(info, columns=column_names)
df.to_csv('H:\Web_scrapping\data.csv', index=False)


browser.quit()