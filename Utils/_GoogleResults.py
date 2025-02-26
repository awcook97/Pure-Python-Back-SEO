import requests
from bs4 import BeautifulSoup
from typing import List


def init_GoogleResults(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix

class GoogleResults():
	def __init__(self):
		self.SESSION = requests.Session()
		self.URL = "https://www.google.com/search"
		self.HEADERS = {
			'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
			" AppleWebKit/537.36 (KHTML, like Gecko) "
			"Chrome/84.0.4147.135 Safari/537.36"
		}
	def extract_related_questions(self, document: BeautifulSoup) -> List[str]:
		div_questions = document.find_all("div", class_="related-question-pair")
		get_text = lambda a: a.text.split('Search for:')[0]
		if not div_questions:
			return []
		questions = list(map(get_text, div_questions))
		return questions

	def search(self, keyword: str, proxy, numresults: int = 10):
		params = {"q": keyword, "num": numresults}
		try:
			response = self.SESSION.get(self.URL, params=params, headers=self.HEADERS, proxies=proxy, timeout=10)
		except Exception as e:
			#print("Google Search Failed", e)
			return str(e)
		if response.status_code != 200:
			#print("Google Search Failed")
			return str(f'Status Code isn\'t 200. Status code: {response.status_code}')
		self.response = BeautifulSoup(response.text, "html.parser")
		try:
			self.extract_related_questions(self.response)
		finally: return self.response

	def pullCompetition(self, myTerm: str, proxy: dict, numResults: int = 10) -> dict():
		"""searches myTerm, if found, returns the competition

		Args:
			myTerm (str): The search term to search for.

		Raises:
			Exception: Failure to parse the search result.

		Returns:
			_type_: A dictionary of the competitors and their links.
		"""
		document = self.search(myTerm, proxy, numResults)
		if not document: print('no doc'); return {}
		if type(document) is str:
			return document
		try:
			return dict(self.extractCompetition(document))
		except Exception:
			raise Exception

	def extractCompetition(self, myDoc: BeautifulSoup) -> dict():
		"""Summary: reads search result and returns all of the competitors of that search term.
		Args:
			myDoc (BeautifulSoup): SERP

		Returns:
			competitors: a dictionary of the competitors and their links.
		"""
		competitors = {}
		findResults = myDoc.find('div', id='search') #->type: NavigableString
		links = findResults.find_all('a')
		rank = 1
		for link in links:
			linkURL = link.get('href')
			linkText = link.find('h3')
			if not linkText:
				continue
			linkText = linkText.string
			competitors[linkURL] = rank
			rank += 1
			
		return competitors
