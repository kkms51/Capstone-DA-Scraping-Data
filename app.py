from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

# don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # do not change this

# insert the scraping here
base_url = 'https://boardgamegeek.com/browse/boardgame/page/'

games = []

for page in range(1, 11):
    url = f'{base_url}{page}'
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content, "html.parser")
    table = soup.find('table', {'class': 'collection_table'})
    rows = table.find_all('tr', {'id': lambda x: x and x.startswith('row_')})
    
    for row in rows:
        name = row.find('td', {'class': 'collection_objectname'}).a.text.strip()
        rating = row.find('td', {'class': 'collection_bggrating'}).text.strip()
        num_voters = row.find_all('td', {'class': 'collection_bggrating'})[2].text.strip()
        games.append((name, rating, num_voters))
        
# insert data wrangling here
df = pd.DataFrame(games, columns=['Name', 'Rating', 'Num_Voters'])
df['Rating'] = df['Rating'].astype(float)
df['Num_Voters'] = df['Num_Voters'].str.replace(',', '').astype(int)

# end of data wrangling 

@app.route("/")
def index(): 
    # Calculate mean rating
    card_data = f'{df["Rating"].mean().round(2)}' 

    # Generate plot
    fig, ax = plt.subplots(figsize=(20, 9))
    df.plot(kind='bar', x='Name', y='Rating', ax=ax, legend=False)
    ax.set_title('Board Game Ratings')
    ax.set_xlabel('Game Name')
    ax.set_ylabel('Rating')
    plt.xticks(rotation=90)

    # Rendering plot
    figfile = BytesIO()
    plt.savefig(figfile, format='png', transparent=True)
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    plot_result = str(figdata_png, 'utf-8')

    # Render to HTML
    return render_template('index.html',
        card_data=card_data, 
        plot_result=plot_result
    )

if __name__ == "__main__": 
    app.run(debug=True)
