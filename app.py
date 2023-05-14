from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import datetime
import os
os.environ['TZ'] = 'Asia/Jakarta'
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this


mapping = {
    'South Jakarta': 'Jakarta Selatan', 
    'West Jakarta': 'Jakarta Barat', 
    'North Jakarta': 'Jakarta Utara', 
    'East Jakarta':'Jakarta Timur', 
    'Jakarta':'Jakarta Pusat', 
    'South Tangerang': 'Tangerang Selatan', 
    'Bandung Kota':'Bandung', 
    'Bandung Kabupaten':'Bandung', 
    'Bogor Kota':'Bogor', 
    'Central Jakarta': 'Jakarta Pusat', 
    'Central Jakarta City': 
    'Jakarta Pusat', 
    'Central Lampung': 
    'Lampung', 
    'Kota Jakarta Barat': 'Jakarta Barat', 
    'Kota Jakarta Pusat':'Jakarta Pusat', 
    'Kota Jakarta Selatan':'Jakarta Selatan'}

def get_past_date(str_days_ago):
    TODAY = datetime.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return str(TODAY.isoformat())
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return str(date.isoformat())
    elif splitted[1].lower() in ['minute', 'minutes', 'mins', 'min', 'm']:
        return str(TODAY.isoformat())
    elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
       return str(TODAY.isoformat())
    elif splitted[1].lower() in ['day', 'days', 'd']:
        if splitted[0].isdigit():
            date = TODAY - relativedelta(days=int(splitted[0]))
            return str(date.isoformat())
        else:
            date = TODAY - relativedelta(days=int(1))
            return str(date.isoformat())
    elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
        if splitted[0].isdigit():
            date = TODAY - relativedelta(weeks=int(splitted[0]))
            return str(date.isoformat())
        else:
            date = TODAY - relativedelta(weeks=int(1))
            return str(date.isoformat())
    elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
        if splitted[0].isdigit():
         date = TODAY - relativedelta(months=int(splitted[0]))
         return str(date.isoformat())
        else:
         date = TODAY - relativedelta(months=int(1))
         return str(date.isoformat())
    elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
        if splitted[0].isdigit():
            date = TODAY - relativedelta(years=int(splitted[0]))
            return str(date.isoformat())
        else:
            date = TODAY - relativedelta(years=int(1))
            return str(date.isoformat())
    else:
        return "Wrong Argument format"

def function_scrapping(page = 1):
    # Inisiasi awal
    base_url = 'https://www.kalibrr.id/job-board/te/data/'
    url_get = requests.get(base_url + str(1))
    soup = BeautifulSoup(url_get.content,"html.parser")

    #  Total Page 
    total_page = int(soup.find('ul', {"class" : "k-flex k-justify-center k-items-center k-my-8"}).find_all('li')[-2].get_text())
    print(f"Total Page : {total_page}")

    # inisiasi list kosong
    temp = [] #initiating a list
   
    print(f"Start Scrapping {base_url}")

    page_scrap = page if page > 1 else total_page
    for i in range(1, page_scrap + 1):
        progress = round((i / page_scrap) * 100) # untuk menampilkan presentasi progress pada terminal
        
        print(f"{progress}% | page {i} dari {page_scrap} Pages")

        url = 'https://www.kalibrr.id/job-board/te/data/' + str(i)
        url_get = requests.get(url)
        soup = BeautifulSoup(url_get.content,"html.parser")
    
        list_job = soup.find_all('div', {'itemscope': True, 'itemtype' : 'http://schema.org/ListItem','itemprop' : "itemListElement"})

        for item in list_job:
            # nama pekerjaan terdapat pada tag h2 > a
            job_title = item.select_one('h2 a').get_text().strip()
            # tanggal post kita tag turunan beserta class nya kemudian kita ekstrak test dan split ambil index 0 dan replace Posted, kemudian convert
            post_date = datetime.strptime(
                get_past_date(
                item.select_one("div.k-col-start-5 span:first-of-type").text.strip().split("•")[0].strip().replace("Posted", "")
                ), 
                "%Y-%m-%dT%H:%M:%S.%f"
                ).strftime('%Y-%m-%d %H:%M:%S').split()[0] + ""
            # deadline kita tag turunan beserta class nya kemudian kita ekstrak test dan split ambil index 1 dan replace Apply before kemudian + tahun sekarang, kemduain ganti format agar sama dengan tanggal post diatas
            date_posting = item.select_one("div.k-col-start-5 span:first-of-type").text.strip().split("•")[1].strip().replace("Apply before", "").strip() + " " + str(datetime.now().year)
            deadline_date = datetime.strptime(date_posting, '%d %b %Y') + timedelta(days=1)
            deadline_date = deadline_date.strftime('%Y-%m-%d %H:%M:%S').split()[0] + ""
            # lokasi kota kita ambil tag turunan beserta class nya lalu ambil text kemudian ambil index [0], kita replace bahasa kota yang belum sesuai dengan mapping
            nama_kota = item.select_one("div.k-col-start-3 div.k-flex > a").text.strip().split(",")[0]
            nama_kota_new = nama_kota.replace(nama_kota, mapping.get(nama_kota, nama_kota))
            # lokasi negara kita ambil tag turunan beserta class nya lalu ambil text kemudian ambil index [1]
            country = item.select_one("div.k-col-start-3 div.k-flex > a").text.strip().split(",")[1].strip()
          

          
            # print(f"Nama Pekerjaan : {job_title}")
            # print(f'Tanggal Post : {post_date}') 
            # print(f"Tanggal Deadline : {deadline_date}")
            # print(f'Lokasi Kota : {nama_kota_new}')
            # print(f'Lokasi Negara : {country}')
            # print("\n")
    
            temp.append({
                "job_title" : job_title,
                "city" : nama_kota_new,
                "country" : country,
                "date_post": post_date,
                "date_deadline": deadline_date
            })


    return pd.DataFrame(temp)

    # df.to_csv('kalibrr-job-list.csv', index=False)
	


@app.route("/")
def index(): 
	url_page = requests.get('https://www.kalibrr.id/job-board/te/data/1')
	soup_page = BeautifulSoup(url_page.content,"html.parser")
	total_page = int(soup_page.find('ul', {"class" : "k-flex k-justify-center k-items-center k-my-8"}).find_all('li')[-2].get_text())
	data = function_scrapping(total_page) 
	data_indonesia = data[data['country'] == 'Indonesia'] # ambil negara indonesia saja
	data_grouped = pd.DataFrame(data_indonesia['city'].value_counts())
	# generate plot
	ax = data_grouped.plot(kind='bar', title='Chart Lowongan Berdasarkan Kota', figsize = (20,15))
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = data_grouped, 
		plot_result=plot_result,
		total_page=total_page,
		date_now = datetime.now()
		)


if __name__ == "__main__": 
    app.run(debug=True)