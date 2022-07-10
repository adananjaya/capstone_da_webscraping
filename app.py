from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-list'}).find_all('div',attrs={'class':'lister-item mode-advanced'})

row_length = len(table)

temp = [] #init
n = 200 #banyaknya judul yang ingin diambil kelipatan 50
j = 1

while j < 200: #data yang digunakan saat ini adalah 200 Judul
    url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31&start='+str(j)+'&ref_=adv_nxt')
    soup = BeautifulSoup(url_get.content,"html.parser")
    table = soup.find('div', attrs={'class':'lister-list'}).find_all('div',attrs={'class':'lister-item-content'})
    j = j + 50

    for i in range(0, row_length):
    
        #get Title 
        Title = table[i].find('h3', attrs={'class':'lister-item-header'}).find('a').text.strip()
    
        try:
            #get Rating
            Rating = table[i].find('div', attrs={'class':'inline-block ratings-imdb-rating'}).text.strip()
        except AttributeError:
            Rating = 0
 
        try:
            #get meta score
            Meta_Score = table[i].find('div', attrs={'class':'inline-block ratings-metascore'}).find('span').text.strip()
        except AttributeError:
            Meta_Score = 0
        
        try:
            #get votes
            Votes = table[i].find('p', attrs={'class':'sort-num_votes-visible'}).find('span', attrs={'name':'nv'}).\
            text.strip().replace(",","")
        except AttributeError:
            Votes = 0
    
        temp.append((Title,Rating,Meta_Score,Votes)) 
    

#change into dataframe
df = pd.DataFrame(temp, columns = ('Title','Rating','Meta_Score','Votes'))

#insert data wrangling here
df[['Rating','Meta_Score']] = df[['Rating','Meta_Score']].astype('float64')
df['Votes'] = df['Votes'].astype('int64')

Top20Film = df[df['Meta_Score'] != 0].sort_values(by='Votes').tail(20)
Top20Series = df[df['Meta_Score'] == 0].sort_values(by='Votes').tail(20)
Top20Film['Meta_Score'] = Top20Film['Meta_Score']/10
Top20Film['Meta_Rating'] = Top20Film['Rating'] + Top20Film['Meta_Score']
Top20Film = Top20Film.set_index('Title')
Top20Series = Top20Series.set_index('Title')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Votes"].mean().round(2)}' #be careful with the " and ' 

	# generate plot Tujuh film populer
	ax = Top20Film.tail(7).plot(kind = 'barh', y = 'Votes', 
                   rot = 0, color = ['r','g','b','c','m','y','k'], 
                   legend=False,xlabel = ' ',figsize = (20,9), fontsize = '8')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# generate plot Tujuh film rekomendasi
	bx = Top20Film.sort_values(by='Meta_Rating').tail(7).plot(kind = 'barh', 
                                            y = 'Meta_Rating', rot = 0, 
                                            color = ['r','g','b','c','m','y','k'], 
                                            legend=False, xlabel = '',figsize = (20,9), fontsize = '8')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result1 = str(figdata_png)[2:-1]

	# generate plot Tujuh series populer
	bx = Top20Series.tail(7).plot(kind = 'barh', y = 'Votes', 
                   rot = 0, color = ['r','g','b','c','m','y','k'], 
                   legend=False,xlabel = ' ', figsize = (20,9), fontsize = '8')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1]

		# generate plot Tujuh series rekomendasi
	bx = Top20Series.sort_values(by='Rating').tail(7).plot(kind = 'barh', 
                                            y = 'Rating', rot = 0, 
                                            color = ['r','g','b','c','m','y','k'], 
                                            legend=False, xlabel = '',figsize = (20,9), fontsize = '8')
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result3 = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result, # plot film populer
		plot_result1=plot_result1, # plot film rekomendasi
		plot_result2=plot_result2, # plot series populer
		plot_result3=plot_result3 # plot series rekomendasi
		)


if __name__ == "__main__": 
    app.run(debug=True)