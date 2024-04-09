from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
import time
import threading
import math

def getMovies(pageNumStart,pageNumEnd,file):

    for pageNum in range(pageNumStart,pageNumEnd):
        url = base_url + f"?page={pageNum}"

        req = Request(url, headers={'User-Agent': 'XYZ/3.0'})
        uClient = urlopen(req)
        page_html = uClient.read()
        uClient.close() 
            
        page_soup = soup(page_html, 'html.parser')   
        containers = page_soup.find_all('div', {'class':'card style_1'})

        for container in containers:
            title = container.div.div.a['title']
            content = container.find('div', class_ ='content')
            score = content.div.div.div['data-percent']
            date = content.find('p').text

            file.write(title + ',' + score + ',' + date + '\n')
      

base_url = 'https://www.themoviedb.org/movie'
filename1 = "movie_without_thread.csv"
filename2 = "movie_with_thread.csv"
file1 = open(filename1, 'a')
file2 = open(filename2, 'a')

headers = "Title, Score, Date\n"
file1.write(headers)
file2.write(headers)

def scrapeWithThread(num_of_pages):
    num_of_threads = 6
    thread_list= []

    for i in range(num_of_threads):
        start = math.floor(i*(num_of_pages / num_of_threads)) + 1
        end = math.floor((i+1)* (num_of_pages / num_of_threads)) + 1
        thread_list.append(threading.Thread(target=getMovies,args=(start,end,file2)))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
    file2.close()

def scrapeWithoutThread(num_of_pages):
    getMovies(1,num_of_pages+1,file1)
    file1.close()
    
num_of_pages = 36
start_time = time.time()
print("Scraping Movies without thread. Please wait...")
scrapeWithoutThread(num_of_pages)
end_time = time.time()
print(f"time without thread: {end_time-start_time}")

start_time = time.time()
print("Scraping Movies with thread. Please wait...")
scrapeWithThread(num_of_pages)
end_time = time.time()
print(f"time with thread: {end_time - start_time}")

