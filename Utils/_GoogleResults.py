import urllib3
from bs4 import BeautifulSoup
from multiprocessing import pool
import functools
from Utils._Scraperz import getResponses, PageAudit, CompareAudit
from playwright.sync_api import sync_playwright, Browser
from urllib.parse import urlencode, quote_plus

class GoogleResults:
    def __init__(
        self, executor: pool.Pool, query: str, numResults: int = 10, proxy: str = ""
    ):
        self.URL = "https://www.google.com/search"
        self.proxy = proxy
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.135 Safari/537.36"
        }

        if proxy.startswith("http"):
            try:
                phd = proxy.split("://")[1].split("@")
                ph = phd[0].split(":")
                default_headers = urllib3.make_headers(
                    proxy_basic_auth=f"{ph[0]}:{ph[1]}"
                )
                purl = f"http://{phd[1]}"
                self.sesh = urllib3.ProxyManager(
                    purl, headers=self.HEADERS, proxy_headers=default_headers
                )
                # testiez = self.sesh.request("GET", "https://api.ipify.org?format=json")
                # print(testiez.data.decode('utf-8'))
            except Exception:
                self.sesh = urllib3.PoolManager()
        else:
            self.sesh = urllib3.PoolManager()
            # self.proxy = None
        self.executor = executor
        self.query = query
        self.numResults = numResults
        self.urls = list()
        self.deets = dict()
        self.relatedQuestions = list()
        # self.search()

    def search(self):
        params = {"q": self.query, "num": self.numResults}
        # startTime = time.time()
        try:
            # self.response = self.sesh.request(
            #     "GET", self.URL, headers=self.HEADERS, fields=params
            # )
            with sync_playwright() as p:
                # Launch a Firefox browser instance (set headless=True for headless mode)
                browser: Browser = p.firefox.launch(
                    headless=True,
                    args=["--start-maximized"],
                    downloads_path="output",
                    ignore_default_args=[
                        "--mute-audio",
                        "--hide-scrollbars",
                        "--disable-infobars",
                        "--disable-notifications",
                        "--disable-dev-shm-usage",
                        "--disable-webgl",
                        "--disable-xss-auditor",
                        "--disable-accelerated-2d-canvas",
                    ],            
                )
                context = browser.new_context(user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0")
                page = context.new_page()
                params = {"q": self.query, "num": self.numResults}
                url = 'https://google.com/search?' + urlencode(params, quote_via=quote_plus)
                page.goto(url, wait_until="networkidle")
                content = page.content()
        except Exception:
            # print(e)
            return False
        # if self.response.status != 200:
        #     return False
        # self.soup = BeautifulSoup(self.response.data, "html.parser")
        self.soup = BeautifulSoup(content, "html.parser")
        findRes = self.soup.find("div", id="search")
        if not findRes:
            clickLink = self.soup.find("a").get("href")
            try:
                self.response = self.sesh.request(
                    "GET", f"https://google.com{clickLink}", headers=self.HEADERS, fields=params
                )
            except Exception:
                # print(e)
                return False
            if self.response.status != 200:
                return False
            self.soup = BeautifulSoup(self.response.data, "html.parser")
        self.relatedQuestions = self.extract_related_questions(self.soup)
        # print(f"Time to get RelQs: {time.time() - startTime}")
        self.extract_urls()
        # print(f"Time to get URLs: {time.time() - startTime}")
        self.myInfoz = self.mgetResp()
        # print(f"Time to get All sites: {time.time() - startTime}")
        presend = list()
        for url, resp in self.myInfoz:
            presend.append(((url, resp), self.query, self.deets[url]["rank"]))
        # print(f"Time to get put shit into list: {time.time() - startTime}")
        self.audDict = dict()
        self.audList = self.executor.starmap(PageAudit, presend)
        # print(f"Time to get all audit pages: {time.time() - startTime}")
        for aud in self.audList:
            self.audDict[aud.url] = aud
        # print(f"Time to get audits in a dict: {time.time() - startTime}")
        self.audits = CompareAudit(self.audDict)
        self.audits.addPAA(self.relatedQuestions)
        # print(f"Time to get compare audit: {time.time() - startTime}")
        return self.audits

    def extract_urls(self):
        findRes = self.soup.find("div", id="search")
        links = findRes.find_all("a")
        rank = 1
        for link in links:
            linkURL = link.get("href")
            linkText = link.find("h3")
            if not linkText:
                continue
            linkText = linkText.string
            self.deets[linkURL] = {"rank": rank, "title": linkText}
            self.urls.append(linkURL)
            rank += 1

    def extract_related_questions(self, document: BeautifulSoup) -> list:
        div_questions = document.find_all("div", class_="related-question-pair")
        get_text = lambda a: a.text.split("Search for:")[0]
        if not div_questions:
            return []
        questions = list(map(get_text, div_questions))
        return questions

    def mgetResp(self):  # , urls: list, proxy: str=""):
        urlz = dict()
        for i in range(self.executor._processes):
            urlz[i] = list()
        maxz = len(self.urls)
        i = 0
        for url in self.urls:
            if str(url).endswith(
                (
                    "xml",
                    "gz",
                    "pdf",
                    "jpg",
                    "png",
                    "gif",
                    "jpeg",
                    "svg",
                    "css",
                    "js",
                    "ico",
                )
            ):
                continue
            urlz[i % self.executor._processes].append(url)
            i += 1
            if i == maxz:
                i = 0
        self.rd = self.executor.map(
            functools.partial(getResponses, proxy=self.proxy), list(urlz.values())
        )
        fg = list()
        for r in self.rd:
            while len(r) > 0:
                fg.append(r.popitem())
        return fg

