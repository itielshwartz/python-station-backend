# Python station backend
# About
* The backend behind : [python-station]

* Full data pipeline to scrape <http://planetpython.org> 

* Output: Every Github (Python) project featured on the history of planetpython.
 
* Also includes data enrichment using Github + Reddit + Hackernews APi.

## How does it work?
1. Download the pages from planetPython.org clone

2. Use [BeautifulSoup] to transform raw page into posts

2. Use [Github API] to get basic project data (And filter no python projects)
 
 4. Use [Praw] (Reddit) + [HN Api] + [Github Trending] to enrich data
 
 5. Show data using [Github pages + Vue.js]
 



# How to run?
  - Clone the project
  - `python3 -m venv ./venv && source venv/bin/activate && pip install -r requirements.txt`
  - `venv/bin/python pipeline.py --pages-to-download 5`
  - To download Reddit data you need to fill in your reddit creds in: `requests_utils.py`
  - If you get limit on your Github requests you need to fill in your Github creds in: `requests_utils.py`
  
# Pipeline Flow chart
```
+-------------------+
| Download Pages    |
+---------+---------+
          |
+---------v---------+
|Transform to Posts |
+---------+---------+
          |
+---------v---------+
|Extract projects   |
+---------+---------+
          |
+---------v---------+
|Enrich Using Apis  |
+---------+---------+
          |
+---------v----------+
|Deploy Using Github |
| Pages              |
+--------------------+
```


### Development

Want to contribute? Great!
Feel free to open PR/Issue :)

License
----

MIT - **Free Software, Hell Yeah!**

[//]: #URLs

   [python-station]: <http://python-station.etlsh.com/>
   [nginx]: <https://www.nginx.com/resources/wiki/>
   [BeautifulSoup]: <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>
   [Github API]: <https://developer.github.com/v3/>
   [Praw]: <https://github.com/praw-dev/praw>
   [HN Api]: <https://github.com/HackerNews/API>
   [Github Trending]: <https://github.com/trending/python?since=daily>
   [Github pages + Vue.js]: https://github.com/itielshwartz/python-station-website

