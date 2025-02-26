from multiprocessing import Pool
import asyncio
import aiohttp
async def getSesh(url: str, proxy: str, sesh: aiohttp.ClientSession):
	myResponse = ""
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
	conn = aiohttp.TCPConnector(limit=None, limit_per_host=0)
	async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(15.0, 15.0), headers=headers, connector_owner=False) as sesh:
		tasks = []
		for url in urls:
			if not url or not url.startswith("http"):
				continue
			tasks.append(getSesh(url, proxy, sesh))
		
		results = await asyncio.gather(*tasks)
		
		for url, result in results:
			res[url] = result
	conn.close()
	return res

def getResponses(nw: dict) -> dict:
	urls = nw["urls"]
	proxy = nw["proxy"]
	loop = asyncio.new_event_loop()
	results = loop.run_until_complete(agetResponses(urls, proxy)) # type: dict
	loop.run_until_complete(asyncio.sleep(0.25))
	loop.close()
	return results

def mgetResp(urls: list, proxy: str):
	nw = list()
	td = dict()
	td["proxy"] = proxy
	td["urls"] = list()
	count = 0
	for url in urls:
		td["urls"].append(url)
		count += 1
		if count == 10:
			count = 0
			nw.append(td.copy())
			
			td["urls"] = list()
	if len(td["urls"]): nw.append(td.copy())
	with Pool() as pool:
		myR = pool.map(getResponses, nw)
	rd = dict()
	for i in myR:
		rd.update(i)
	return rd
def init_mFastURLs(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix
# if __name__ == "__main__":
# 	myURLs = [
# 		"https://asq.org/quality-resources/learn-about-standards",
# 		"https://www.educationworld.com/standards/",
# 		"https://www.nationalartsstandards.org/",
# 		"https://www.mdpi.com/journal/standards",
# 		"https://thinkculturalhealth.hhs.gov/clas/standards",
# 		"https://pcaobus.org/oversight/standards",
# 		"https://dese.mo.gov/college-career-readiness/curriculum/missouri-learning-standards",
# 		"https://www.ada.gov/law-and-regs/design-standards/2010-stds/",
# 		"https://www.loc.gov/librarians/standards",
# 		"https://www.standardsit.com/",
# 		"https://www.ifc.org/en/insights-reports/2012/ifc-performance-standards",
# 		"https://www.dictionary.com/browse/standards",
# 		"https://www.gapsc.com/",
# 		"https://www.ifrs.org/groups/international-sustainability-standards-board/",
# 		"https://www.tn.gov/education/districts/academic-standards.html",
# 		"https://www.theiia.org/en/standards/what-are-the-standards/mandatory-guidance/standards/",
# 		"https://www.sba.gov/federal-contracting/contracting-guide/size-standards",
# 		"https://standardsmap.org/",
# 		"https://www.cde.state.co.us/standardsandinstruction",
# 		"https://www.okcps.org/domain/1702",
# 		"https://cea-accredit.org/about-cea/standards",
# 		"https://www.sae.org/standards",
# 		"https://www.wpath.org/publications/soc",
# 		"http://www.nfpa.org/Codes-and-Standards",
# 		"https://nafme.org/publications-resources/standards/",
# 		"https://www.irs.gov/businesses/small-businesses-self-employed/national-standards-food-clothing-and-other-items",
# 		"https://www.msche.org/standards/",
# 		"https://www.shopulstandards.com/",
# 		"https://www.opm.gov/policy-data-oversight/classification-qualifications/general-schedule-qualification-standards/",
# 		"https://www.youtube.com/watch?v=rpdmPj7WPuQ",
# 		"https://www.whitehouse.gov/omb/information-regulatory-affairs/statistical-programs-standards/",
# 		"https://www2.archivists.org/standards",
# 		"https://www.who.int/tools/child-growth-standards",
# 		"https://www.access-board.gov/ada/",
# 		"https://www.apprenticeship.gov/employers/registered-apprenticeship-program/register/standards-builder",
# 		"https://www.socialstudies.org/standards/national-curriculum-standards-social-studies-introduction",
# 		"https://www.etsi.org/standards",
# 		"https://education.ohio.gov/Topics/Learning-in-Ohio/OLS-Graphic-Sections/Learning-Standards",
# 		"https://www.historians.org/jobs-and-professional-development/statements-standards-and-guidelines-of-the-discipline/statement-on-standards-of-professional-conduct",
# 		"https://www.gasb.org/",
# 		"https://nap.nationalacademies.org/catalog/18409/developing-assessments-for-the-next-generation-science-standards",
# 		"http://www.epsb.ky.gov/",
# 		"https://www.apa.org/science/programs/testing/standards",
# 		"https://www.faa.gov/training_testing/testing/test_standards",
# 		"https://www.dpi.nc.gov/districts-schools/classroom-resources/academic-standards/standard-course-study",
# 		"https://www.time.gov/",
# 		"https://diabetesjournals.org/care/issue/46/Supplement_1",
# 		"https://www.pmi.org/pmbok-guide-standards/foundational",
# 		"https://books.google.com/books?id=BKS6FK1567IC&pg=RA3-PA2&lpg=RA3-PA2&dq=standards&source=bl&ots=pFfTH8mpZz&sig=ACfU3U1_7sYCSRNN9kPcmt8F_n5r494Zqw&hl=en&sa=X&ved=2ahUKEwip5NGM5s6BAxVrkGoFHXO9CYAQ6AF6BQjQAhAD",
# 		"https://books.google.com/books?id=sw1tGil7sUwC&pg=PA24&lpg=PA24&dq=standards&source=bl&ots=scOz46bq5M&sig=ACfU3U303hm3VKQ4w9WajQF2LSSAqG_wLg&hl=en&sa=X&ved=2ahUKEwip5NGM5s6BAxVrkGoFHXO9CYAQ6AF6BQjPAhAD"
# 	]
# 	import time
# 	initTime = time.time()
# 	
# 	fastTime = time.time()
# 	