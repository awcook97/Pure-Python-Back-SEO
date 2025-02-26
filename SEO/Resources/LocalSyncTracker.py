from geopy.geocoders import Nominatim
from BackSEODataHandler import getBackSEODataHandler
import asyncio
from playwright.async_api import Playwright, async_playwright, expect, Browser, Page, Locator
import os
import json
import time
from typing import List
def cleanFilename(s: str):
	if not s:
		return ''
	badchars = '\\/:*?\"\'<>|'
	s = s.encode('ascii', 'ignore').decode('ascii')
	for c in badchars:
		s = s.replace(c, '')
	return s

def listtoDict(tl: List[List[dict]]) -> dict:
	"""accepts an unknown amount of lists with dicts inside. EX:
 			List[List[dict],List[dict],[List[List[dict],List[dict]]]]
		returns single dict.
		"""
	newthing = dict()
	for things in tl:
		if type(things) is list:
			newthing.update(listtoDict(things))
		elif type(things) is dict:
			for key, val in things.items():
				newthing[key] = val
	return newthing

def runLocations(keyword: str, gridSpace: int, locat: str, proxy: str="") -> dict:
	loc = Nominatim(user_agent="GetLoc")
	if keyword == "" or locat == "":
		return {"error":"keyword or location not set"}
	getLoc = loc.geocode(locat)
	lati = getLoc.latitude
	longi = getLoc.longitude
	dh = getBackSEODataHandler()
	dh.saveData("Local", "location", (lati, longi))
	if not os.path.exists(f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}"):
		os.makedirs(f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}")
	outputPath = f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}"
	latMile = 0.0144927536231884
	longMile = 0.0181818181818182
	gslat = latMile * gridSpace
	gslong = longMile * gridSpace
	# +-      +0      ++
	# 0-      00      0+
	# --      -0      +-
	directions = [
		(gslat,		-gslong,	"NW"),	(gslat,  0,	"N"),	(gslat,  gslong, "NE"),
		(0,			-gslong,	"W"),	(0,		 0,	"C"),	(0,		 gslong,  "E"),
		(-gslat,	-gslong,	"SW"),	(-gslat, 0,	"S"),	(-gslat, gslong, "SE")
	]
	executor = dh.getPool()
	prepList = list()
	for direction in directions:
		prepList.append((direction, lati, longi, keyword, outputPath, proxy))
	almost = executor.starmap(runProcessorPlaywright, prepList)
	thesuper = listtoDict(almost)
	thesuper["keyword"] = keyword
	thesuper["location"] = locat
	with open(f"{outputPath}/businessList.json", "w") as f:
		json.dump(thesuper, f, indent=4)
	
	dh.savenoupdate("Local", "data", thesuper)
	dh.savenoupdate(f"Local_{keyword}", f"{time.time()}", thesuper)
	return thesuper

def runProcessorPlaywright(direction: tuple, lati: float, longi: float, keyword: str, outputPath: str, proxy: str=""):
	loop = asyncio.new_event_loop()
	try:
		myi = loop.run_until_complete(doLocStuff(direction, lati, longi, keyword, outputPath, proxy))
	finally:
		loop.close()
	return myi

async def doLocStuff(direction: tuple, lati: float, longi: float, keyword: str, outputPath: str, proxy: str=""):
	proxybreak: None | dict = None
	if proxy != "":
		spl = proxy.split("@")
		ty= spl[0].split("://")[0]
		usr, pas = spl[0].split("://")[1].split(":")
		ip, port = spl[1].split(":")
		proxybreak = {}
		#if len(spl) == 4: proxybrok = {"type": spl[0], "user": spl[1], "pass": spl[2], "host": spl[3], "port": spl[4]}
		#if len(spl) == 3: proxybrok = {"type": spl[0], "user": "", "pass": "", "host": spl[1], "port": spl[2]}
		proxybreak ={"server": f"{ty}://{ip}:{port}", 
					"username": usr, 
					"password": pas
					}
	async with async_playwright() as playwright:
		browser = await playwright.chromium.launch(
			headless=True, 
			args=[
				"--start-maximized"
			],
			downloads_path="output",
			ignore_default_args=[
				"--mute-audio", 
				"--hide-scrollbars", 
				"--disable-infobars", 
				"--disable-notifications", 
				"--disable-dev-shm-usage",
				"--disable-webgl", 
				"--disable-xss-auditor",
				"--disable-accelerated-2d-canvas"
			],
			proxy=proxybreak)
		if not os.path.exists(outputPath):
			os.makedirs(outputPath)
		try:
			return await runloc(browser=browser, lati=lati + direction[0], longi=longi + direction[1],keyword=keyword, outputPath=f"{outputPath}/{direction[2]}", direction=direction[2])
		except Exception as e:
			return {direction[2]:{"error":[f"{str(e)}",""], "all":["",""]}}

async def runloc(browser: Browser, lati: float, longi: float, keyword: str, outputPath: str, direction="") -> dict:
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	with open(f"{outputPath}/info.saudit", "w") as f:
		f.write(f"lati: {lati}\nlongi: {longi}\nkeyword: {keyword}\noutputPath: {outputPath}\ndirection: {direction}\n")
	context = await browser.new_context(geolocation={"latitude":lati,"longitude":longi}, locale="en-US", permissions=["geolocation"])
	page = await context.new_page()
	await context.route("https://www.google.com/maps/vt?pb", lambda route: route.abort())
	await page.goto("https://www.google.com/maps")
	await page.get_by_label("Your Location").click()
	await page.get_by_role("textbox", name="Search Google Maps").fill(keyword)
	await page.locator("#searchboxinput").press("Enter")
	await page.get_by_label("Show Your Location").click()
	await page.get_by_role("button", name="Search", exact=True).click()
	startTime = time.time()
	
	businessList = dict()
	businessList["all"] = list()
	count = 0
	while time.time() - startTime < 15 and len(businessList) < 20:
		for dd in await page.get_by_role("feed").get_by_role("link").filter(has_not=page.get_by_alt_text("Website")).filter(has_not_text="Visit Site").all():
			name =  await dd.get_attribute("aria-label")
			linkz = await dd.get_attribute("href")
			if name in businessList: continue
			count+=1
			rank = count
			scpath = f"{outputPath}/RANK_{rank}_{cleanFilename(name)}.png"
			await dd.screenshot(path=scpath)
			businessList[name] = {"rank":rank,"link":linkz,"screenshot":scpath}
		await page.get_by_role("feed").press("PageDown")
	businessList["all"] = list(businessList.keys())
	businessList["all"].remove("all")
	with open(f"{outputPath}/businessList.json", "w") as f:
		json.dump(businessList, f, indent=4)
	await context.close()
	return {direction:businessList}

