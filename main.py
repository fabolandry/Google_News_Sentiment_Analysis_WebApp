from flask import Flask, request, render_template
from textblob import TextBlob
import requests, re
from bs4 import BeautifulSoup
from pprint import pprint


app = Flask(__name__)
@app.route('/', methods=['GET','POST'])
def rootpage():
    # Declaring the variable that will be transferred to Html
    finalsub = None
    finalsent = None
    newsp = []
    if request.method == 'POST' and 'search-term' in request.form:
        SearchTerm = request.form.get('search-term')
        if SearchTerm:
            print(SearchTerm)
            a = Analysis(SearchTerm)
            a.run()
            print(a.term, 'Subjectivity: ', a.subjectivity, 'Sentiment: ', a.sentiment)
            finalsub = a.subjectivity
            finalsent = a.sentiment
            newsp = a.news
    return render_template("index.html", finalsub=finalsub, finalsent=finalsent, newsp=newsp)

class Analysis:
    def __init__(self, term):
        self.term = term
        self.subjectivity = 0
        self.sentiment = 0
        self.news = []
        self.url = 'https://www.google.com/search?q={0}&source=lnms&tbm=nws'.format(self.term)

    def run(self):
            response = requests.get(self.url)
            # print(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')
            mainDiv = soup.find("div", {"id": "main"})
            posts = [i for i in mainDiv.children][3:-2]

            for post in posts:
                reg = re.compile(r"^/url.*")
                cursor = post.findAll("a", {"href": reg})
                postData = {}
                postData["headline"] = cursor[0].find("div").get_text()
                postData["source"] = cursor[0].findAll("div")[1].get_text()
                postData["timeAgo"] = cursor[1].next_sibling.find("span").get_text()
                postData["description"] = cursor[1].next_sibling.find("span").parent.get_text().split("· ")[1]
                self.news.append(postData)
            pprint(self.news)
            for h in self.news:
                blob = TextBlob(h["headline"] + " " + h["description"])
                self.sentiment += blob.sentiment.polarity / len(self.news)
                self.subjectivity += blob.sentiment.subjectivity / len(self.news)

app.run( debug=True)
