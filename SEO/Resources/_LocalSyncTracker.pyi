from geopy.geocoders import Nominatim
from BackSEODataHandler import getBackSEODataHandler
import asyncio
from playwright.async_api import (
    Playwright,
    async_playwright,
    expect,
    Browser,
    Page,
    Locator,
)
import os
import json
import time
from typing import List, Any

def listtoDict(tl: List[List[dict]]) -> dict: ...
def runLocations(keyword: str, gridSpace: int, locat: str, proxy: str = "") -> dict: ...
def runProcessorPlaywright(
    direction: tuple,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    proxy: str = "",
) -> dict | dict[Any, dict[str, list[str]]]: ...
async def doLocStuff(
    direction: tuple,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    proxy: str = "",
) -> dict | dict[Any, dict[str, list[str]]]: ...
async def runloc(
    browser: Browser,
    lati: float,
    longi: float,
    keyword: str,
    outputPath: str,
    direction="",
) -> dict: ...
