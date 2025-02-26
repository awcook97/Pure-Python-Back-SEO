import asyncio
from playwright.async_api import Playwright, async_playwright, expect, Browser, Page, Locator
from geopy.geocoders import Nominatim
import re
import time
import os
import json
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
from typing import List
from BackSEODataHandler import getBackSEODataHandler
def cleanFilename(s):
	if not s:
		return ''
	badchars = '\\/:*?\"\'<>|'
	for c in badchars:
		s = s.replace(c, '')
	return s

async def run(playwright: Playwright, keyword: str, lati: float, longi: float, gridSpace: int, locat: str, proxy: str="") -> None:
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
		[(gslat,	-gslong,	"NW"),	(gslat,  0,	"N"),	(gslat,  gslong, "NE")],
		[(0,		-gslong,	 "W"),	(0,		 0,	"C"),	(0,		 gslong,  "E")],
		[(-gslat,	-gslong,	"SW"),	(-gslat, 0,	"S"),	(-gslat, gslong, "SE")]
	]
	# directions = [
	# 	[(gslat,	-gslong,	"NW"),	(gslat,  gslong, "NE")],#	(gslat,  0,	"N"),	(gslat,  gslong, "NE")],
	# 	[(0.0,		 0.0,		"C"),],#		(0,		 gslong,  "E")],
	# 	#[(-gslat,	gslong,		"SE"),]#	(-gslat, 0,	"S"),	]
	# ]
	#browser = await playwright.chromium.launch(headless=False)
	#tasks = [doLocStuff(browser, lati + direction[0], longi + direction[1], keyword, f"{outputPath}/{direction[2]}") for direction in directions]
	loop = asyncio.get_event_loop()
	tasks = list()
	with ProcessPoolExecutor() as executor:
		for direction in directions:
			tasks.append(loop.run_in_executor(executor, pdoLocStuff, direction, lati, longi, keyword, f"{outputPath}", proxy))
	thesuper = await asyncio.gather(*tasks)
	
	#await browser.close()
	with open(f"{outputPath}/businessList.json", "w") as f:
		json.dump(thesuper, f, indent=4)
	#newthing = await listtoDict(thesuper)
	#print(json.dumps(newthing, indent=4))
	return thesuper

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

def pdoLocStuff(directions: list, lati: float, longi: float, keyword: str, outputPath: str, proxy: str=""):
	loop = asyncio.new_event_loop()
	try:
		myi = loop.run_until_complete(doLocStuff(directions, lati, longi, keyword, outputPath, proxy))
	finally:
		loop.close()
	return myi
	#return asyncio.run(doLocStuff(directions, lati, longi, keyword, outputPath))

async def doLocStuff(directions: list, lati: float, longi: float, keyword: str, outputPath: str, proxy: str=""):
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
		browser = await playwright.chromium.launch(headless=True, args=["--start-maximized"], downloads_path="output",
													ignore_default_args=["--mute-audio", "--hide-scrollbars", "--disable-infobars", "--disable-notifications", 
																	"--disable-dev-shm-usage", "--disable-webgl", "--disable-xss-auditor", "--disable-accelerated-2d-canvas"],
													proxy=proxybreak)
		tasks = [doLocStuff1(browser=browser, lati=lati + direction[0], longi=longi + direction[1],keyword=keyword, outputPath=f"{outputPath}/{direction[2]}", direction=direction[2]) for direction in directions]
		thesuper = await asyncio.gather(*tasks)
		await browser.close()
	return thesuper

async def doLocStuff1(browser: Browser, lati: float, longi: float, keyword: str, outputPath: str, direction: str="") -> dict:
	if not os.path.exists(outputPath):
		os.makedirs(outputPath)
	try:
		return await runloc(browser, lati, longi, keyword, outputPath, direction)
	except Exception as e:
		return {direction:{"error":[f"{str(e)}",""], "all":["",""]}}

async def zoomAllIn(page: Page):
	page.get_by_role("slider").click
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)
	await page.get_by_role("button", name="Zoom in").click(delay=10, force=True)

async def zoomOut14z(page: Page):
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)
	await page.get_by_role("button", name="Zoom out").click(delay=100, force=True)

async def runloc(browser: Browser, lati: float, longi: float, keyword: str, outputPath: str, direction="") -> dict:
	context = await browser.new_context(geolocation={"latitude":lati,"longitude":longi}, locale="en-US", permissions=["geolocation"])
	page = await context.new_page()
	await context.route("https://www.google.com/maps/vt?pb", lambda route: route.abort())
	await page.goto("https://www.google.com/maps")
	await page.get_by_label("Your Location").click()
	#await page.get_by_role("textbox", name="Search Google Maps").click()
	await page.get_by_role("textbox", name="Search Google Maps").fill(keyword)
	await page.locator("#searchboxinput").press("Enter")
	#await zoomAllIn(page)
	#await zoomOut14z(page)
	await page.get_by_label("Show Your Location").click()
	await page.get_by_role("button", name="Search", exact=True).click()
	#await page.get_by_label("Search this area").click()
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
			await dd.screenshot(path=f"{outputPath}/{cleanFilename(name)}.png")
			businessList[name] = {"rank":rank,"link":linkz}
		await page.get_by_role("feed").press("PageDown")
	businessList["all"] = list(businessList.keys())
	businessList["all"].remove("all")
	with open(f"{outputPath}/businessList.json", "w") as f:
		json.dump(businessList, f, indent=4)
	await context.close()
	return {direction:businessList}
 #	
	# for stuff in done:
	# 	name =  await stuff.get_attribute("aria-label")
	# 	linkz = await stuff.get_attribute("href")
	# 	businessList["all"].append({"name":name, "link":linkz})
  #	startTime = time.time()
	# count = 0
	# while True:
	# 	mystuff = await page.get_by_role("feed").get_by_role("link").filter(has_not=page.get_by_alt_text("Website")).filter(has_not_text="Visit Site").all()
	# 	if len(done) > 20 or time.time() - startTime > 120: break
	# 	nStartTimes = time.time()
	# 	for stuff in mystuff:
	# 		# some of these might not have a rating
	# 		if time.time() - nStartTimes > 120:
	# 			break
	# 		business = dict()
	# 		try:
	# 			business["name"] = await stuff.get_attribute("aria-label")
	# 		except:
	# 			continue
	# 		if not business["name"]: continue
	# 		if business["name"] in done:
	# 			continue
	# 		if business["name"].endswith("website"): continue
	# 		if business["name"].startswith("ad "): continue
	# 		done.append(business["name"])
	# 		count+=1
	# 		business["rank"] = count
	# 		await stuff.first.scroll_into_view_if_needed()
	# 		await stuff.click(force=True, delay=1000)
	# 		# #await stuff.click()
	# 		try:
	# 			#await page.get_by_role("main", name=business["name"]).screenshot(path=f"{outputPath}/{cleanFilename(business['name'])}.png", timeout=300)
	# 			if not page.is_enabled(page.get_by_role("main", name=business["name"])):
	# 				await stuff.click(force=True, delay=1000)
	# 			if not page.is_enabled(page.get_by_role("main", name=business["name"])):
	# 				continue
	# 			business["info"] = await page.get_by_role("main", name=business["name"]).get_by_label(":").all_text_contents()
	# 			await page.get_by_role("main", name=business["name"]).press("PageDown")
	# 			business["more_info"] = await page.get_by_role("main", name=business["name"]).get_by_label(":").all_text_contents()
	# 			business["website"] = await page.get_by_role("main", name=business["name"]).get_by_label("Website:").all_text_contents()
	# 			business["address"] = await page.get_by_role("main", name=business["name"]).get_by_label("Address:").all_text_contents()
	# 			business["phone"] = await page.get_by_role("main", name=business["name"]).get_by_label("Phone:").all_text_contents()
	# 			await page.get_by_role("main", name=business["name"]).get_by_label("Close", exact=True).scroll_into_view_if_needed()
	# 			await page.get_by_role("main", name=business["name"]).get_by_label("Close", exact=True).click(delay=300, force=True, no_wait_after=True)
	# 		finally:
	# 			businessList.append(business)

			
	# 	await page.get_by_role("feed").press("End")
	# businessList.append({"all": done})
	# with open(f"{outputPath}/businessList.json", "w") as f:
	# 	json.dump(businessList, f, indent=4)
	# for b in businessList:
	# 	print(b)
	
	# # ---------------------
	# await context.close()
	# return {direction:businessList}


async def doLocalRankTracker(keyword: str = "", locat: str = "", distanceBetweenNodes: int = 25, proxy: str = "") -> dict:
	loc = Nominatim(user_agent="GetLoc")
	if keyword == "" or locat == "":
		return {"error":"keyword or location not set"}
	getLoc = loc.geocode(locat)
	lat = getLoc.latitude
	longi = getLoc.longitude
	getBackSEODataHandler().saveData("Local", "location", (lat, longi))
	async with async_playwright() as playwright:
		omg = await run(playwright, keyword, getLoc.latitude, getLoc.longitude, distanceBetweenNodes, locat, proxy)
	realdeal = listtoDict(omg)
	getBackSEODataHandler().saveData("Local", "data", realdeal)
	getBackSEODataHandler().saveData(f"Local_{keyword}", f"{time.time()}", realdeal)
	return realdeal

def loadLocalRankTracker() -> dict:
	return getBackSEODataHandler().loaddata("Local", "data")

def runLocalRankTracker(keyword: str = "", locat: str = "", distanceBetweenNodes: int = 25, proxy: str = "") -> dict:
	loop = asyncio.new_event_loop()
	myi: dict = dict()
	try:
		myi = loop.run_until_complete(doLocalRankTracker(keyword, locat, distanceBetweenNodes=distanceBetweenNodes, proxy=proxy))
	except Exception as e:
		myi["Error"] = [f"{str(e)}", ""]
	finally:
		loop.close()
		return ("core", "Local", "update", myi)

if __name__ == "__main__":
	freeze_support()
	asyncio.run(doLocalRankTracker("pest control", "San Diego, CA"))
