import requests
from bs4 import BeautifulSoup as soup
from pathlib import Path
import time
import threading
import math
import csv
import os

def save_img(img_link, author, category,mode):
    res = requests.get(img_link,headers={'User-Agent': 'XYZ/3.0'})
    if res.status_code == 200:
        main_path_thread = Path('Main_Thread')
        main_path_noThread = Path('Main_noThread')
        if(mode == 't'):
            main_path = main_path_thread
        else:
            main_path = main_path_noThread
        main_path.mkdir(parents=True,exist_ok=True)
        aut_cat_path = main_path / author / category
        aut_cat_path.mkdir(parents= True, exist_ok = True)
        file_name = img_link.split('/')[-1]
        file_path = aut_cat_path / file_name
        with open(file_path,'wb') as file:
            file.write(res.content)
def create_csv(title,author,tags,img_file,size,mode):
    file_path_thread = 'img_info_thread.csv'
    file_path_noThread = 'img_info_noThread.csv'
    if(mode == 't'):
        file_path = file_path_thread
    else:
        file_path = file_path_noThread
    if not os.path.exists(file_path):
        with open(file_path,mode='w',newline='') as file:
            csv_writer = csv.writer(file)
            headers = ['Title','Photographer','Tags','Image URL','Size']
            csv_writer.writerow(headers)
    with open(file_path, mode='a',newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([title,author,tags,img_file,size])
     
def scraping(img_pages,start,finish,mode):
          
    for i in range(start,finish):
        res_author = requests.get(img_pages[i],headers={'User-Agent': 'XYZ/3.0'})
        if res_author.status_code == 200:
            page_soup_author = soup(res_author.content, 'html.parser')
            media_actions = page_soup_author.find('div', class_='media-actions')
            title = media_actions.a['title'][9:]
            img_file = media_actions.a['href']
            media_details = page_soup_author.find('ul', class_= 'media-details').find_all('li')
            author = media_details[0].strong.a['title']
            category = media_details[1].strong.span.a.text
            if mode == 'nt':
                photographers[author] = photographers.get(author,0) + 1
                categories[category] = categories.get(category,0) + 1
            size = media_details[2].strong.text
            lis = page_soup_author.find('ul', class_='keyword-tags').find_all('li')
            tags = []
            for li in lis:
                tags.append(li.get_text(strip=True))
            print("Saving",title,'with thread' if mode =='t' else 'with_out_thread',"...")
            create_csv(title,author,tags,img_file,size,mode)
            save_img(img_file,author,category,mode)
    

def scrapeWithThreads(numOfImages):
    numOfThreads = 4
    thread_list= []
    for i in range(numOfThreads):
        start = math.floor(i*(numOfImages / numOfThreads)) 
        end = math.floor((i+1)* (numOfImages / numOfThreads))
        thread_list.append(threading.Thread(target=scraping,args=(img_pages,start,end,'t')))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
        
def scrapeWithoutThreads(numOfImages):
    scraping(img_pages,0,numOfImages,'nt')

      
img_pages = []
base_url = "https://isorepublic.com/"
categories = {}
photographers = {}

res = requests.get(base_url,headers={'User-Agent': 'XYZ/3.0'})
if res.status_code == 200:
    page_soup = soup(res.content, 'html.parser')
    containers = page_soup.find_all('a',{'class':'photo-grid-item'})
    for container in containers:
        img_page = container['href']
        img_pages.append(img_page)
        
numOfImages = len(img_pages)

start_time = time.time()
scrapeWithThreads(numOfImages)
threadTime = time.time() - start_time

start_time = time.time()
scrapeWithoutThreads(numOfImages)
nonThreadTime = time.time() - start_time

print('----------------------------------')
print("Number of photos by photograph")
for photographer in photographers:
    print(photographer,':',photographers[photographer])
print('----------------------------------')
print("Number of photos by categories")
for category in categories:
    print(category,':',categories[category])
    
print('----------------------------------')
print('Time with thread:',threadTime)
print('Time without thread:',nonThreadTime)


