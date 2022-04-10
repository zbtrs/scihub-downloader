from bs4 import BeautifulSoup
import requests
from flask import Flask, redirect, url_for, request
from selenium import webdriver
from flask import Flask

app = Flask(__name__)

BAIDUXUESHU_URL = 'https://xueshu.baidu.com/'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
}
class ScholarConf:
    """Helper class for global settings."""

    VERSION = '2.10'
    LOG_LEVEL = 1
    MAX_PAGE_RESULTS = 10  # Current default for per-page results
    SCHOLAR_SITE = 'http://scholar.google.com'

    # USER_AGENT = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
    # Let's update at this point (3/14):
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'

    # If set, we will use this file to read/save cookies to enable
    # cookie use across sessions.
    COOKIE_JAR_FILE = None

class Scihub(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.available_base_url_list = self._get_available_scihub_urls()
        self.base_url = self.available_base_url_list[0] + '/'

    def _get_available_scihub_urls(self):
        urls = []
        res = self.sess.request(method='GET',url = 'http://tool.yovisun.com/scihub/')
        s = self._get_soup(res.content)
        for a in s.find_all('a',href=True):
            if 'sci-hub.' in a['href']:
                urls.append(a['href'])
        return urls

    def get_proxies(self,proxy):
        if proxy:
            return {
                "http": proxy,
                "https": proxy,
            }
        return None

    def _get_soup(self,html):
        return BeautifulSoup(html,'html.parser')

    def doi_download_url(self,doi):
        scihuburl = self.base_url + doi
        driver = webdriver.Chrome()
        driver.get(scihuburl)
        driver.implicitly_wait(10)
        s = self._get_soup(driver.page_source)
        location = s.find(name='button').attrs['onclick']
        download_url = self.base_url + location[16:-1]
        return download_url

    def search_doi(self,title):  #从百度学术上搜索一篇文献的DOI
        def fetch_doi(url):
            res = self.sess.request(method='GET', url=url)
            s = self._get_soup(res.content)
            dois = [doi.text.replace("DOI：", "").replace("ISBN：", "").strip() for doi in
                    s.find_all('div', class_='doi_wr')]
            if dois:
                return dois[0]
            else:
                return ""
        driver = webdriver.Chrome()
        driver.get('https://xueshu.baidu.com/s?wd=' + title + '&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8&sc_hit=1')
        driver.implicitly_wait(10)
        s = self._get_soup(driver.page_source)
        location = s.find('h3',class_ ="t c_font")
        paper_url = location.find('a').attrs['href']
        return fetch_doi(paper_url)
        """
        start = 0
        results = []
        while True:
            try:
                res = self.sess.request(method='GET', url=BAIDUXUESHU_URL,
                                        params={'wd': ' ' + title, 'pn': start, 'filter': 'sc_type%3D%7B1%7D'})
            except requests.exceptions.RequestException as e:
                print('Failed to complete search with query %s (connection error)' % title)
                return results
            print(res.content)
            s = self._get_soup(res.content)
            papers = s.find_all('div', class_="result")

            for paper in papers:
                if not paper.find('table'):
                    link = paper.find('h3', class_='t c_font')
                    url = str(link.find('a')['href'].replace("\n", "").strip())
                    return fetch_doi(url)
        """


    def fetch_doi(self,url):
        res = self.sess.request(method='GET', url=url)
        s = self._get_soup(res.content)
        dois = [doi.text.replace("DOI：", "").replace("ISBN：", "").strip() for doi in
                s.find_all('div', class_='doi_wr')]
        if dois:
            return dois[0]
        else:
            return ""

    def title_download_url(self,title):
        doi = self.search_doi(title)
        return self.doi_download_url(doi)


    def get_download_url(self,value,opt):
        if opt == 1:
            return self.doi_download_url(value)
        else:
            return self.title_download_url(value)

    def get_base_url(self):
        print(self.base_url)

@app.route("/doi",methods = ['POST'])
def geturl_doi():
    sh = Scihub()
    url = sh.get_download_url(request.form['doi'],1)
    return 'get it!',200,{"url" : url}

@app.route("/keywords",methods = ['POST'])
def geturl_keywords():
    sh = Scihub()
    url = sh.get_download_url(requests.form['keywords'],2)
    return 'get it!',200,{"url" : url}

"""
def main():
    sh = Scihub()
    print(sh.get_download_url('Deep Convolutional - Optimized Kernel Extreme Learning Machine Based Classifier for Face Recognition',2))

if __name__ == '__main__':
    main()
"""

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=80,
        debug=False
    )