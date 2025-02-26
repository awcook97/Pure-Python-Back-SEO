from multiprocessing.pool import Pool
from geopy.geocoders import Nominatim
from BackSEODataHandler import BackSEODataHandler, getBackSEODataHandler
import asyncio
from playwright.async_api import (
    Playwright,  # noqa: F401
    async_playwright,
    expect,  # noqa: F401
    Browser,
    BrowserContext,
    Page,
    Locator,
)
import os
import json
import time
from typing import List, Any
# import cython


def init_LocalSyncTracker(name):
    try:
        suffix = b"_" + name.encode("ascii")
    except UnicodeEncodeError:
        suffix = b"U_" + name.encode("punycode").replace(b"-", b"_")
    return b"PyInit" + suffix


def cleanFilename(s: str):
    if not s:
        return ""
    badchars = "\\/:*?\"'<>|&"
    s = s.encode("ascii", "ignore").decode("ascii")
    for c in badchars:
        s = s.replace(c, "")
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


def runLocations(keyword: str, gridSpace: int, locat: str, proxy: str = "") -> dict:
    loc = Nominatim(user_agent="GetLoc")
    if keyword == "" or locat == "":
        return {"error": "keyword or location not set"}
    getLoc = loc.geocode(locat)
    if not getLoc:
        return {"error": "location not found"}
    lati: float = getLoc.latitude
    longi: float = getLoc.longitude
    dh: BackSEODataHandler = getBackSEODataHandler()
    dh.saveData("Local", "location", (lati, longi))
    if not os.path.exists(
        f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}"
    ):
        os.makedirs(
            f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}"
        )
    outputPath: str = (
        f"output/screenshots/{cleanFilename(locat)}/{cleanFilename(keyword)}"
    )
    latMile: float = 0.0144927536231884
    longMile: float = 0.0181818181818182
    gslat: float = latMile * gridSpace
    gslong: float = longMile * gridSpace
    # +-      +0      ++
    # 0-      00      0+
    # --      -0      +-
    directions: List[tuple] = [
        (gslat, -gslong, "NW"),
        (gslat, 0, "N"),
        (gslat, gslong, "NE"),
        (0, -gslong, "W"),
        (0, 0, "C"),
        (0, gslong, "E"),
        (-gslat, -gslong, "SW"),
        (-gslat, 0, "S"),
        (-gslat, gslong, "SE"),
    ]
    executor: Pool = dh.getPool()
    prepList = list()
    for direction in directions:
        prepList.append((direction, lati, longi, keyword, outputPath, proxy))
    almost: list = executor.starmap(runProcessorPlaywright, prepList)
    thesuper: dict = listtoDict(almost)
    thesuper["keyword"] = keyword
    thesuper["location"] = locat
    with open(f"{outputPath}/businessList.json", "w") as f:
        json.dump(thesuper, f, indent=4)

    dh.savenoupdate("Local", "data", thesuper)
    dh.savenoupdate(f"Local_{keyword}", f"{time.time()}", thesuper)
    return thesuper


def runProcessorPlaywright(
    direction: tuple,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    proxy: str = "",
) -> dict | dict[Any, dict[str, list[str]]]:
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    try:
        myi: dict = loop.run_until_complete(
            doLocStuff(direction, lati, longi, keyword, outputPath, proxy)
        )
    finally:
        loop.close()
    return myi


async def doLocStuff(
    direction: tuple,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    proxy: str = "",
) -> dict | dict[Any, dict[str, list[str]]]:
    proxybreak: None | dict = None
    if proxy != "" and proxy != None and "@" in proxy and ":" in proxy:
        spl: list[str] = proxy.split("@")
        ty: str = spl[0].split("://")[0]
        usr, pas = spl[0].split("://")[1].split(":")
        ip, port = spl[1].split(":")
        proxybreak = {}
        # if len(spl) == 4: proxybrok = {"type": spl[0], "user": spl[1], "pass": spl[2], "host": spl[3], "port": spl[4]}
        # if len(spl) == 3: proxybrok = {"type": spl[0], "user": "", "pass": "", "host": spl[1], "port": spl[2]}
        proxybreak = {"server": f"{ty}://{ip}:{port}", "username": usr, "password": pas}
    async with async_playwright() as playwright:
        # browser: Browser = await playwright.chromium.launch(
        #     # executable_path="chromium-1084\chrome-win\chrome.exe",
        #     headless=False,
        #     args=["--start-maximized"],
        #     downloads_path="output",
        #     ignore_default_args=[
        #         "--mute-audio",
        #         "--hide-scrollbars",
        #         "--disable-infobars",
        #         "--disable-notifications",
        #         "--disable-dev-shm-usage",
        #         "--disable-webgl",
        #         "--disable-xss-auditor",
        #         "--disable-accelerated-2d-canvas",
        #     ],
        #     proxy=proxybreak,
        # )
        browser: Browser = await playwright.firefox.launch(
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
            proxy=proxybreak,
        )
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        try:
            return await runloc(
                browser=browser,
                lati=lati + direction[0],
                longi=longi + direction[1],
                keyword=keyword,
                outputPath=f"{outputPath}/{direction[2]}",
                direction=direction[2],
            )
        except Exception as e:
            return {direction[2]: {"error": [f"{str(e)}", ""], "all": ["", ""]}}


async def runloc(
    browser: Browser,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    direction: str = "",
) -> dict:
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    with open(f"{outputPath}/info.saudit", "w") as f:
        f.write(
            f"lati: {lati}\nlongi: {longi}\nkeyword: {keyword}\noutputPath: {outputPath}\ndirection: {direction}\nSearch: https://www.google.com/maps/search/{keyword}/@{lati},{longi},12.37z"
        )
    context: BrowserContext = await browser.new_context(
        geolocation={"latitude": lati, "longitude": longi},
        locale="en-US",
        permissions=["geolocation"],
        bypass_csp=True,
        
    )
    # print(lati)
    # print(longi)
    page: Page = await context.new_page()
    await context.route(
        "https://www.google.com/maps/vt?pb", lambda route: route.abort()
    )
    await context.route(
        "https://www.google.com/gen_204", lambda route: route.abort()
    )
    await context.route(
        "https://play.google.com/", lambda route: route.abort()
    )
    await page.goto(f"https://www.google.com/maps/search/{keyword}/@{lati},{longi},12.37z")
    # https://www.google.com/maps/search/plumbing/@38.9105314,-97.441379,12.37z
    # await page.get_by_label("Search Google Maps").click()
    # await page.get_by_label("Search Google Maps").fill(keyword)
    # await page.locator("#searchboxinput").press("Enter")
    # await page.get_by_role("button", name="Search", exact=True).click()

    # await page.get_by_label("Show Your Location").click(delay=500)
    # await page.get_by_role("button", name="Search", exact=True).click(delay=2000)
    # await page.get_by_label("Show Your Location").click(delay=3000)
    # await page.get_by_label("Search this area").click(delay=1000)
    startTime: float = time.time()
    #print(startTime)
    businessList = dict()
    businessList["all"] = list()
    count: int = 0
    while time.time() - startTime < 15 and len(businessList) < 50:
        dd: Locator
        # print("Made dd")
        feedlocator = await page.locator("h1", has_not_text="Sponsored").first.inner_text()
        # print(f"there's a feed locator {feedlocator}")
        if feedlocator != "Results":
            scpath: str = f"{outputPath}/RANK_1_{feedlocator}.png"
            await page.screenshot(path=scpath)
            businessList[feedlocator] = {"rank": 1, "link": "https://maps.google.com", "screenshot": scpath}
            break
        if feedlocator == "Results":
            for dd in (
                await page.get_by_role("feed")
                .get_by_role("link")
                .filter(has_not=page.get_by_alt_text("Website"))
                .filter(has_not_text="Visit Site")
                .filter(has_not_text="")
                .filter(has_not_text="BOOK ONLINE")
                .all()
            ):
                name: str = await dd.get_attribute("aria-label") or ""
                name = cleanFilename(name)
                linkz: str = await dd.get_attribute("href") or ""
                if name in businessList:
                    continue
                if not name or name == "" or not linkz or linkz == "":
                    continue
                count += 1
                rank: int = count
                scpath: str = f"{outputPath}/RANK_{rank}_{name}.png"
                await dd.screenshot(path=scpath)
                businessList[name] = {"rank": rank, "link": linkz, "screenshot": scpath}
            await page.get_by_role("feed").press("PageDown")
    businessList["all"] = list(businessList.keys())
    businessList["all"].remove("all")
    with open(f"{outputPath}/businessList.json", "w") as f:
        json.dump(businessList, f, indent=4)
    await page.close()
    await context.close()
    return {direction: businessList}

# runLocations()