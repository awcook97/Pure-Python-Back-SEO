import urllib3
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup as bs
from multiprocessing import pool, freeze_support
from bs4 import BeautifulSoup
import regex
try:
	from Utils._Rake import _Rake
	from Utils._textstat import textstat
	from Utils import CustomThread
except:
	from _Rake import _Rake
	from _textstat import textstat
import json
from typing import Dict
import time
import asyncio
import aiohttp
from threading import Thread

def init_SiteMap(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix

class CustomThread(Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
		Thread.__init__(self, group, target, name, args, kwargs)
		self._return = None
	def run(self):
		if self._target is not None:
			self._return = self._target(*self._args, **self._kwargs)
	def join(self, *args):
		Thread.join(self, *args)
		return self._return

def workerinit(prox=""):
	global wproxy
	wproxy = prox

def getPage(url: str):
	global wproxy
	#print(wproxy)
	
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
	if wproxy.startswith('http'): http = urllib3.ProxyManager(wproxy, headers=headers)
	else: http = urllib3.PoolManager(headers=headers)
	#print(url)

	response = http.request('GET', url, timeout=60.0)
	if response.status != 200:
		return ("error", f"Status Code: {response.status}")
	sxml = bs(response.data, 'xml')
	psml = list()
	if len(sxml.find_all("sitemap")):
		for page in sxml.find_all("sitemap"):
			#print(page)
			psml.append(page.find("loc").text)
		#print(psml)
		return ("sitemap", psml)
	for pp in sxml.find_all("loc"):
		psml.append(pp.text)
	return ("url", psml)

async def getSesh(url: str, proxy: str, sesh: aiohttp.ClientSession):
	myResponse = ""
	global wproxy
	proxy = wproxy
	try:
		async with sesh.get(url, proxy=proxy) as sresponse:
			myResponse = await sresponse.text()
	except Exception as e:
		myResponse = f"FAILURE: {e}"
	finally:
		return (url, myResponse)

async def agetResponses(urls: list, proxy: str) -> dict:
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
	res = dict()
	#conn = aiohttp.TCPConnector(limit=None, limit_per_host=0)
	async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(15.0, 15.0), headers=headers,) as sesh:
		tasks = []
		for url in urls:
			if not url or not url.startswith("http"):
				continue
			tasks.append(getSesh(url, proxy, sesh))
		
		results = await asyncio.gather(*tasks)
		
		for url, result in results:
			res[url] = result
	# conn.close()
	return res

def getResponses(urls: list, proxy="") -> dict:
	loop = asyncio.new_event_loop()
	results = loop.run_until_complete(agetResponses(urls, proxy)) 
	loop.run_until_complete(asyncio.sleep(0.25))
	loop.close()
	return results

class PageAudit:
	def __init__(self, url: tuple, main_keyword: str = "", rank=0, *args, **kwargs) -> None:
		if len(args):
			if args[0] == True:
				self.fromJson(args[1])
		else:
			self.errors = list()
			self.rank = rank
			self.url, content = url
			self._theBS = BeautifulSoup(content, "lxml")
			self.main_keyword = main_keyword
			
			self.build()

	def build(self):
		self.title = self.getTitle()
		self.article = self.getArticle()
		self.article_keywords = CustomThread(target=self.get_article_keywords,)
		self.article_keywords.start()
		self.readability_score = CustomThread(target=self.get_readability_score,)
		self.readability_score.start()
		self.relevance_score = CustomThread(target=self.get_relevance_score,)
		self.relevance_score.start()
		self.inbound_links = self.get_inbound_links()
		self.outbound_links = self.get_outbound_links()
		self.schema = self.getSchema()
		self.images = self.getImages()
		self.meta_tags = self.get_meta_tags()
		self.article_outline = self.get_article_outline()
	   #self.headers = self.headers
		self.length = self.get_length()
		self.relevance_score = self.relevance_score.join()
		self.readability_score = self.readability_score.join()
		self.article_keywords = self.article_keywords.join()
		self.keyword_count = sorted(self.get_keyword_count(), key=lambda x: x['Occurences'], reverse=True)
		
	   #self.grade_level


		if len(self.main_keyword) < 2:
			try:
				self.main_keyword = self.keyword_count[0]['Keyword']
			except:
				self.main_keyword = ""
		delattr(self, "_theBS")

	def fromJson(self, myJson):
		self.rank = myJson["rank"]
		self.url = myJson["url"]
		self.main_keyword = myJson["main_keyword"]
		self.title = myJson["title"]
		self.article = myJson["article"]
		self.images = myJson["images"]
		self.meta_tags = myJson["meta_tags"]
		self.article_outline = myJson["article_outline"]
		self.headers = myJson["headers"]
		self.length = myJson["length"]
		self.article_keywords = myJson["article_keywords"]
		self.keyword_count = myJson["keyword_count"]
		self.readability_score = myJson["readability_score"]
		self.grade_level = myJson["grade_level"]
		self.stats = myJson["stats"]
		self.relevance_score = myJson["relevance_score"]
		self.inbound_links = myJson["inbound_links"]
		self.outbound_links = myJson["outbound_links"]
		self.schema = myJson["schema"]

	def toJson(self):
		self._theBS = "Run through parser"
		return json.dumps(self.__dict__)

	def getSchema(self):
		try:
			return json.loads(self._theBS.find("script", attrs={"type": "application/ld+json"}).text)
		except:
			self.errors.append("schema")
			return {}

	def getTitle(self):
		try:
			return self._theBS.title.text
		except: 
			self.errors.append("title")
			return ""

	def getArticle(self)-> str:
		try:
			soup = self._theBS
			article = ""
			if soup.find('main'):
				
				presoup = soup.find('main')
				for piece in presoup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "table"]):
					article += str(f'{piece.get_text()}\n')
			elif soup.find('h1'):
				fh1 = soup.find('h1')
				for stuff in fh1.find_all_next(string=True):
					article += str(stuff.get_text())
			elif soup.find('h2'):
				fh2 = soup.find('h2')
				for stuff in fh2.find_all_next(string=True):
					article += str(stuff.get_text())
			else:
				article = str(soup.get_text('\n',strip=True))
			return article
		except: 
			self.errors.append("article")
			return ""
			
	def getImages(self) -> list:
		try:
			soup = self._theBS
			imgs = list()
			for img in soup.find_all("img", src=True, alt=True):
				imgs.append({img.get("src"): img.get("alt")})
			return imgs
		except: 
			self.errors.append("images")
			return list()
			
	def get_meta_tags(self) -> dict:
		try:
			soup = self._theBS
			meta_tags = {
				tag.get("name", "").lower(): tag.get("content", "")
				for tag in soup.find_all("meta", attrs={"name": True})
			}
			return meta_tags
		except: 
			self.errors.append("meta_tags")
			return dict()
			
	def get_article_outline(self) -> list:
		try:
			soup = self._theBS
			article_outline = list()
			self.headers = list()
			for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
				if len(heading.get_text().strip()) > 2:
					article_outline.append(f"{heading.name}: {' '.join(heading.get_text().strip().split())}")
					self.headers.append(f"{' '.join(heading.get_text().strip().split())}")
			return article_outline
		except: 
			self.errors.append("article_outline")
			return list()
			
	def get_length(self) -> int:
		try:
			self.length = self.article.count(' ')
			return self.length
		except: 
			self.errors.append("length")
			return 0

	def get_article_keywords(self) -> list:
		try:
			myRake = _Rake(include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=0)
			myRake2 = _Rake(include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=1)
			myRake3 = _Rake(include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=2)
			myT = self.article
			myL = list()
			myRake.extract_keywords_from_text(myT)
			myRake2.extract_keywords_from_text(myT)
			myRake3.extract_keywords_from_text(myT)
			myL.extend(myRake.get_ranked_phrases())
			myL.extend(myRake2.get_ranked_phrases())
			myL.extend(myRake3.get_ranked_phrases())
			return list(set(myL))
		except: 
			self.errors.append("article_keywords")
			return list()
			
	def get_keyword_count(self) -> list:
		try:
			article_keywords = self.article_keywords
			article = self.article
			keyword_count = list()
			for keyw in list(set(article_keywords)):
				if article.lower().count(keyw) > 1:
					keyword_count.append({"Keyword":keyw,"Occurences":article.lower().count(keyw)})
			return keyword_count
		except: 
			self.errors.append("keyword_count")
			return list()

	def get_readability_score(self):
		try:
			readability_scored = textstat(self.article)
			readability_score = readability_scored.coleman_liau().score
			self.grade_level = readability_scored.coleman_liau().grade_level
			self.stats = readability_scored.statistics()
			return readability_score
		except: 
			self.errors.append("readability_score")
			self.grade_level = 0.0
			self.stats = dict()
			return 0.0

	def get_relevance_score(self) -> float:
		try:
			main_keyword = self.main_keyword
			main_keyword_lower = main_keyword.lower()
			try:
				spl = main_keyword_lower.split(' ')
				if len(spl) < 2:
					relevancy_score = self.article.lower().count(main_keyword_lower)
					return relevancy_score
				relevancy_score = 0.0
				for n in range(len(spl)):
					for w in range(len(spl)):
						if w + n > len(spl):
							break
						p = ' '.join(spl[w:w+n+1])
						occ = self.article.lower().count(p)
						relevancy_score += float(occ * (n+1/len(spl)))
			except Exception:
				relevancy_score = 0.0
			return relevancy_score
		except:
			self.errors.append("relevance_score")
			return 0.0

	def get_inbound_links(self) -> dict:
		try:
			soup = self._theBS
			inboundLinks = dict()
			for link in soup.find_all("a", href=True):
				linkURL = link.get("href")
				if self.url.split("http")[1].split("://")[1].split("/")[0] not in link.get("href"): 
					if not link.get("href").startswith("#"):
						if not linkURL.startswith("/"): 
							if not linkURL.startswith("."): continue
				linkText = link.get_text().strip()
				try:
					if linkURL.startswith("https"): linkPage = linkURL.split("https://")[1].split("/",1)[1]
					elif linkURL.startswith("http"): linkPage = linkURL.split("http://")[1].split("/",1)[1]
					else: linkPage = linkURL
				except Exception:
					linkPage = linkURL
				if len(linkPage) < 1:
					if linkURL.startswith("https"): linkPage = linkURL.split("https://")[1].split("/",1)[0]
					elif linkURL.startswith("http"): linkPage = linkURL.split("http://")[1].split("/",1)[0]
					else: linkPage = linkURL
				if linkPage not in inboundLinks:
					inboundLinks[linkPage] = dict()
					inboundLinks[linkPage]["linkText"] = list()
				inboundLinks[linkPage]["linkText"].append(linkText)
			return inboundLinks
		except:
			self.inbound_links = dict()
			self.errors.append("inbound_links")

	def get_outbound_links(self) -> dict:
		try:
			soup = self._theBS
			outbound_links = dict()
			for link in soup.find_all("a", href=True):
				if self.url.split("http")[1].split("://")[1].split("/")[0] in link.get("href"): continue
				linkURL = link.get("href")
				if str(linkURL).startswith("#") or linkURL.startswith("/") or linkURL.startswith("."): continue
				if not linkURL.startswith("http"): continue
				linkText = link.get_text().strip()
				if linkURL.startswith("https"): linkDomain= linkURL.split("https://")[1].split("/")[0]
				else: linkDomain= linkURL.split("http://")[1].split("/")[0]
				if linkDomain not in outbound_links: 
					outbound_links[linkDomain] = dict()
					outbound_links[linkDomain]["linkText"] = list()
					outbound_links[linkDomain]["count"] = 0
					outbound_links[linkDomain]["pages"] = list()
					outbound_links[linkDomain]["data"] = list()
				outbound_links[linkDomain]["linkText"].append(linkText)
				outbound_links[linkDomain]["count"] += 1
				outbound_links[linkDomain]["pages"].append(linkURL)
				outbound_links[linkDomain]["data"].append({linkText: linkURL})
			return outbound_links
		except:
			self.outbound_links = dict()
			self.errors.append("outbound_links")
			
class CompareAudit:
	def fj(self, myD: dict, js: bool = False):
		if js: return
		try: self.urls = myD["urls"]
		except: self.urls = list()
		try: self.total_length = myD["total_length"]
		except: self.total_length = 0

		try: self.total_headings = myD["total_headings"]
		except: self.total_headings = 0

		try: self.average_length = myD["average_length"]
		except: self.average_length = 0.0

		try: self.average_header = myD["average_header"]
		except: self.average_header = 0.0

		try: self.bestReadability = myD["bestReadability"]
		except: self.bestReadability = 0.0

		try: self.bestTitle = myD["bestTitle"]
		except: self.bestTitle = "None"

		try: self.bestURL = myD["bestURL"]
		except: self.bestURL = "None"

		try: self.longestNum = myD["longestNum"]
		except: self.longestNum = 0

		try: self.longestArt = myD["longestArt"]
		except: self.longestArt = "None"

		try: self.longestURL = myD["longestURL"]
		except: self.longestURL = "None"

		try: self.common_keywords = myD["common_keywords"]
		except: self.common_keywords = {"None": 0}

		try: self.common_headings = myD["common_headings"]
		except: self.common_headings = {"None": 0}

		try: self.common_oblinks = myD["common_oblinks"]
		except: self.common_oblinks = ["None",]

		try: self.all_headings = myD["all_headings"]
		except: self.all_headings = ["None",]

		try: self.all_keywords = myD["all_keywords"]
		except: self.all_keywords = {"None": 0}

		try: self.all_oblinks = myD["all_oblinks"]
		except: self.all_oblinks = ["None",]

		try: self.numAudits = myD["numAudits"]
		except: self.numAudits = 0

		try: self.main_kw = myD["main_kw"]
		except: self.main_kw = None

		try: self.avgCommonKWs = myD["avgCommonKWs"]
		except: self.avgCommonKWs = [["None", 0],]

		try:
			allURLs = myD["allURLs"]
			self.audits = list()
			for url in allURLs:
				self.audits.append(PageAudit(url, "", "", 0, True, myD[url]))
		except:
			self.audits = None
		return self
		
	def __init__(self, cluster: Dict[str,PageAudit], js: bool=False) -> None:
		if js: 
			self.fj(cluster)
		else:
			self.cluster = cluster
			self.urls = list(self.cluster.keys())
			self.audits = list(self.cluster.values())
			self.find_common()

	def json(self):
		myOd = dict()
		for url in self.urls:
			myOd[url] = self.cluster[url].toJson()
		self.cluster = myOd
		self.audits = myOd
		return json.dumps(self.__dict__)

	def fromJson(file):
		#myD = json.load(open(file, 'r'))
		with open(file, 'r') as f:
			try: auditp1 = json.load(f) #CompareAudit.fromJson(f"output/search_results_audit/{dpg.get_value(self.inspectPicker)}.caudit")
			except: return CompareAudit({"None": PageAudit("None", "", "", 0)})
		p2 = json.loads(auditp1)
		p3 = p2["cluster"]
		p4 = dict()
		for url, audit in p3.items():
			p4[url] = PageAudit(url, "","",0, True, json.loads(audit))
		al = CompareAudit(p4)
		if "people_also_ask" in p2: al.addPAA(p2["people_also_ask"])
		return al
  

	def toJson(self, filename: str):
		myD = dict()
		myD["urls"] = self.urls
		myD["total_length"] = self.total_length
		myD["total_headings"] = self.total_headings
		myD["average_length"] = self.average_length
		myD["average_header"] = self.average_header
		myD["bestReadability"] = self.bestReadability
		myD["bestTitle"] = self.bestTitle
		myD["bestURL"] = self.bestURL
		myD["longestNum"] = self.longestNum
		myD["longestArt"] = self.longestArt
		myD["longestURL"] = self.longestURL
		myD["common_keywords"] = self.common_keywords
		myD["common_headings"] = self.common_headings
		myD["common_oblinks"] = self.common_oblinks
		myD["all_headings"] = self.all_headings
		myD["all_keywords"] = self.all_keywords
		myD["all_oblinks"] = self.all_oblinks
		myD["numAudits"] = self.numAudits
		myD["main_kw"] = self.main_kw
		myD["avgCommonKWs"] = self.avgCommonKWs
		myD["audits"] = list()
		myD["cluster"] = dict()
		if self.audits:
			for audit in self.audits:
				myD["cluster"][audit.url] = dict()
				myD["cluster"][audit.url] = audit.rank
				myD["cluster"][audit.url] = audit.url
				myD["cluster"][audit.url] = audit.main_keyword
				myD["cluster"][audit.url] = audit.title
				myD["cluster"][audit.url] = audit.article
				myD["cluster"][audit.url] = audit.images
				myD["cluster"][audit.url] = audit.meta_tags
				myD["cluster"][audit.url] = audit.article_outline
				myD["cluster"][audit.url] = audit.headers
				myD["cluster"][audit.url] = audit.length
				myD["cluster"][audit.url] = audit.article_keywords
				myD["cluster"][audit.url] = audit.keyword_count
				myD["cluster"][audit.url] = audit.readability_score
				myD["cluster"][audit.url] = audit.grade_level
				myD["cluster"][audit.url] = audit.stats
				myD["cluster"][audit.url] = audit.relevance_score
				myD["cluster"][audit.url] = audit.inbound_links
				myD["cluster"][audit.url] = audit.outbound_links
				myD["cluster"][audit.url] = audit.schema
				myD["audits"].append(audit.toJson())
				myD["cluster"][audit.url] = audit.toJson()
		myD["audits"] = self.audits
		with open(filename, 'w') as f:
			json.dump(myD, f, indent=4)

	def find_common(self):
		self.total_length:int	  = 0
		self.total_headings:int	  = 0
		self.average_length:int	  = 0
		self.average_header:int	  = 0
		self.longestNum: int	  = 0
		self.bestReadability:float= 999999.9
		self.bestTitle: str		  = ""
		self.bestURL: str		  = ""
		self.longestArt: str	  = ""
		self.longestURL: str	  = ""
		self.common_keywords:dict = dict()
		self.common_headings:dict = dict()
		self.all_keywords:dict    = dict()
		self.common_main_kws:dict = dict()
		self.common_oblinks:list  = list()
		self.all_headings:list	  = list()
		self.all_oblinks:list	  = list()
		self.avgCommonKWs:list	  = list()
		self.numAudits: int		  = len(self.audits)

		for aud in self.audits:
			if aud.length > self.longestNum:
				self.longestNum	= aud.length
				self.longestArt = aud.title
				self.longestURL = aud.url
			self.total_length += aud.length
			self.total_headings += len(aud.headers)
			if aud.readability_score < self.bestReadability and aud.readability_score > 1:
				self.bestReadability = aud.readability_score
				self.bestTitle = aud.title
				self.bestURL = aud.url
			if aud.main_keyword not in self.common_main_kws:
				self.common_main_kws[aud.main_keyword] = 0
			self.common_main_kws[aud.main_keyword] += 1
			for kws in aud.keyword_count:
				kw = kws["Keyword"]
				#print(kw)
				if kw in self.all_keywords:
					#print(f"{kw} in all")
					if kw not in self.common_keywords:
						#print(f"{kw} getting dick made")
						self.common_keywords[kw] = dict()
						self.common_keywords[kw]["Pages"] = list()
						self.common_keywords[kw]["Occurences"] = 0
						self.common_keywords[kw]["NumPages"] = 0
					self.common_keywords[kw]["Occurences"] += kws["Occurences"]
					self.common_keywords[kw]["NumPages"] += 1
					self.common_keywords[kw]["Pages"].append(aud.title)
					tempOcc = self.all_keywords[kw][1]
					self.all_keywords[kw] = (kw, kws["Occurences"]+tempOcc)
					#print(f"{kw} got their shit done {self.common_keywords[kw]}")
				else: 
					self.all_keywords[kw] = (kw, kws["Occurences"])


			for h in aud.headers:
				if h in self.all_headings:
					if h not in self.common_headings:
						self.common_headings[h] = dict()
						self.common_headings[h]["Pages"] = list()
						self.common_headings[h]["Occurences"] = 0
					self.common_headings[h]["Occurences"] += 1
					self.common_headings[h]["Pages"].append(aud.title)
				self.all_headings.append(h)

			for link in aud.outbound_links:
				if link in self.all_oblinks:
					if link not in self.common_oblinks: self.common_oblinks.append(link)
				else:
					self.all_oblinks.append(link)
		sorted(self.all_keywords, key=lambda x: x[1], reverse=True)
		try:self.main_kw = sorted(self.common_main_kws, key=lambda x: x, reverse=True)[0]
		except: pass
		for ckw, stats in self.common_keywords.items():
			if stats["NumPages"] == 0: continue
			avgU = stats["Occurences"] / stats["NumPages"]
			self.avgCommonKWs.append((ckw, avgU))
		if len(self.avgCommonKWs) < 5:
			count= 0
			for kw, num in self.all_keywords.items():
				self.avgCommonKWs.append((kw, num[1]))
		if self.numAudits == 0: self.average_header, self.average_length = (1,1)
		else:
			self.average_length = self.total_length / self.numAudits
			self.average_header = self.total_headings / self.numAudits

	def addPAA(self, paa):
		self.people_also_ask = paa
  
	def hasPAA(self):
		return hasattr(self, 'people_also_ask')

class GoogleResults:
	def __init__(self, executor: pool.Pool, query: str, numResults: int = 10, proxy: str = ""):
		self.URL = "https://www.google.com/search"
		self.HEADERS = {
			'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
			" AppleWebKit/537.36 (KHTML, like Gecko) "
			"Chrome/84.0.4147.135 Safari/537.36"
		}
		if proxy != "":
			self.sesh = urllib3.ProxyManager(proxy)
			#self.proxy = {"http": proxy, "https": proxy}
		else:
			self.sesh = urllib3.PoolManager()
			#self.proxy = None
		self.executor = executor
		self.query = query
		self.numResults = numResults
		self.urls = list()
		self.deets = dict()
		self.relatedQuestions = list()
		#self.search()

  
	def search(self):
		params = {"q": self.query, "num": self.numResults}
		startTime = time.time()
		try:
			self.response = self.sesh.request("GET", self.URL, headers=self.HEADERS, fields=params)
		except Exception as e:
			print(e)
			return False
		if self.response.status != 200:
			print(f"Error: {self.response.status}")
			return False
		print(f"Time to get Google response: {time.time() - startTime}")
		self.soup = BeautifulSoup(self.response.data, "html.parser")
		self.relatedQuestions = self.extract_related_questions(self.soup)
		print(f"Time to get RelQs: {time.time() - startTime}")
		self.extract_urls()
		print(f"Time to get URLs: {time.time() - startTime}")
		self.myInfoz = self.mgetResp()
		print(f"Time to get All sites: {time.time() - startTime}")
		presend = list()
		for url, resp in self.myInfoz:
			presend.append(((url, resp), self.query, self.deets[url]["rank"]))
		print(f"Time to get put shit into list: {time.time() - startTime}")
		self.audDict = dict()
		self.audList = self.executor.starmap(PageAudit, presend)
		print(f"Time to get all audit pages: {time.time() - startTime}")
		for aud in self.audList:
			self.audDict[aud.url] = aud
		print(f"Time to get audits in a dict: {time.time() - startTime}")
		self.audits = CompareAudit(self.audDict)
		print(f"Time to get compare audit: {time.time() - startTime}")
		return self.audits

	def extract_urls(self):
		findRes = self.soup.find('div', id='search')
		links = findRes.find_all('a')
		rank = 1
		for link in links:
			linkURL = link.get('href')
			linkText = link.find('h3')
			if not linkText:
				continue
			linkText = linkText.string
			self.deets[linkURL] = {"rank": rank, "title": linkText}
			self.urls.append(linkURL)
			rank += 1

	def extract_related_questions(self, document: BeautifulSoup) -> list:
		div_questions = document.find_all("div", class_="related-question-pair")
		get_text = lambda a: a.text.split('Search for:')[0]
		if not div_questions:
			return []
		questions = list(map(get_text, div_questions))
		return questions

	def mgetResp(self):#, urls: list, proxy: str=""):
		urlz = dict()
		for i in range(self.executor._processes):
			urlz[i] = list()
		maxz = len(self.urls)
		i =0
		for url in self.urls:
			if str(url).endswith(("xml", "gz", "pdf", "jpg", "png", "gif", "jpeg", "svg", "css", "js", "ico")):
				continue
			urlz[i % self.executor._processes].append(url)
			i += 1
			if i == maxz:
				i = 0
		self.rd = self.executor.map(getResponses, list(urlz.values()))
		fg = list()
		for r in self.rd:
			while len(r) > 0:
				fg.append(r.popitem())
		return fg

class SiteMap:
	def __init__(self, url: str, executor: pool.Pool, proxies: list = []):
		'''Class storage handler for sitemaps.
			Initiate the class with the url of the sitemap and a list of proxies.
			Call get sitemaps to get all of the sitemaps.
			The class will then create a process pool, and assign each url to a process.
			Whenever the class receives sitemaps back, it will create more tasks for the process pool.'''
		self.url = url
		self.proxies = proxies
		self.urls = list()
		self.sitemaps = list()
		self.sitemaps.append(url)
		self.prevSitemaps = 0
		self.executor = executor
		self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
		self.netloc = urlparse(url).netloc
		startime = time.time()
		self.get_sitemaps()
		print(f"Time to get sitemaps: {time.time() - startime}")
		rd = self.mgetResp()
		print(f"Time to get responses: {time.time() - startime}")
		self.audict: dict = dict()
		tulist = self.executor.map(PageAudit, rd)
		print(f"Time to get audits: {time.time() - startime}")
		for tu in tulist:
			self.audict[tu.url] = tu
		print(f"Time to get dictofaudits: {time.time() - startime}")
		self.audits = CompareAudit(self.audict)
		print(f"Time to get CompareAudit: {time.time() - startime}")
		# self.wpid = self.get_WP_ids()
		# print(f"Time to get WP ids: {time.time() - startime}")

	def get_sitemaps(self):
		while self.prevSitemaps < len(self.sitemaps) and len(self.urls) < 1000:
			t = self.prevSitemaps
			self.prevSitemaps = len(self.sitemaps)
			self.receiver = self.executor.map(getPage, list(self.sitemaps)[t:])
			for t, r in self.receiver:
				if "sitemap" in t:
					self.sitemaps.extend(r)
				elif "url" in t:
					self.urls.extend(r)
				else:
					continue
				self.sitemaps = list(set(self.sitemaps))
		self.urls = list(set(self.urls[:1000]))
		return self.urls

	def mgetResp(self):#, urls: list, proxy: str=""):
		urlz = dict()
		for i in range(self.executor._processes):
			urlz[i] = list()
		maxz = len(self.urls)
		i =0
		for url in self.urls:
			if str(url).endswith(("xml", "gz", "pdf", "jpg", "png", "gif", "jpeg", "svg", "css", "js", "ico")):
				continue
			urlz[i % self.executor._processes].append(url)
			i += 1
			if i == maxz:
				i = 0
		self.rd = self.executor.map(getResponses, list(urlz.values()))
		fg = list()
		for r in self.rd:
			while len(r) > 0:
				fg.append(r.popitem())
		return fg

	def get_WP_ids(self):
		wpJsonUrl_post = f"https://{self.netloc}/wp-json/wp/v2/posts?per_page=100"
		wpJsonUrl_pages = f"https://{self.netloc}/wp-json/wp/v2/pages?per_page=100"
		postJson = list()
		postJson.extend(self.getWPJson(wpJsonUrl_post))
		##print(postJson)
		pageJson = list()
		pageJson.extend(self.getWPJson(wpJsonUrl_pages))
		return (postJson, pageJson)

	def getWPJson(self, wpJsonUrl):
		headers = {
			#"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9",
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"Pragma": "no-cache",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0",
		}
		http = urllib3.PoolManager()
		try:
			myJsonPostsRequest = http.request('GET', wpJsonUrl, headers=headers, timeout=10.0)
			#print(myJsonPostsRequest.status)
			if myJsonPostsRequest.status != 200:
				##print("request not 200, it's " + myJsonPostsRequest.status_code)
				return list()
			#numPages = myJsonPostsRequest.headers
			###print(myJsonPostsRequest.status_code)
			###print(numPages)
			numPages = int(myJsonPostsRequest.headers['x-wp-totalpages']) - 1
			##print(numPages)
			postJson = myJsonPostsRequest.json()
			#numPages -= 1
			
			while numPages > 0:
				myJsonPostsRequest = http.request('GET', wpJsonUrl, headers=headers, timeout=10.0)
				if myJsonPostsRequest.status == 200: postJson.extend(myJsonPostsRequest.json())
				else: break
				numPages -= 1
			return postJson
		except Exception as e:
			#print("what happened? " + str(e))
			return list()

def omai():
	url = "https://sharetru.com/sitemap.xml"
	myPool = pool.Pool(8, workerinit, ("",))
	#mySitemap = SiteMap(url, executor=myPool)
	# asdf = mySitemap.get_sitemaps()
	# wpshit = mySitemap.get_WP_ids()
	myGoog = GoogleResults(myPool, "SFTP Hosting Service", 100)
	searchz = myGoog.search()
	print(searchz.json())

if __name__ == "__main__":
	freeze_support()
	omai()
	#print(asdf)