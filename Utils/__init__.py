import aiohttp
import asyncio
import json
import regex
import base64
import multiprocessing
import os

try:
    # from Utils.PageAudit import PageAudit, CompareAudit
    # from Utils._Rake import _Rake
    # from Utils._mFastURLs import mgetResp
    from Utils._Scraperz import GoogleResults, PageAudit, CompareAudit

    # from Utils._textstat import textstat
except:
    # from PageAudit import PageAudit, CompareAudit
    # from _mFastURLs import mgetResp
    # from _Rake import _Rake
    from _Scraperz import GoogleResults
from threading import Thread
import pickle
from typing import Any, Dict, Literal
import certifi
import dearpygui.dearpygui as dpg
import time

# from BackSEODataHandler import getBackSEODataHandler
from multiprocessing.pool import Pool
from BackSEODataHandler import getBackSEODataHandler


class CustomThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}) -> None:
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self) -> None:
        if self._target is not None:
            self._return: Any = self._target(*self._args, **self._kwargs)

    def join(self, *args) -> Any:
        Thread.join(self, *args)
        return self._return


def cleanFilename(s) -> Any | str:
    if not s:
        return ""
    badchars = "\\/:*?\"'<>|"
    for c in badchars:
        s = s.replace(c, "")
    return s


def getResponses(nw: dict) -> dict:
    """getResponses({'urls': urls: list, 'proxy': proxy: str})"""
    urls: Any = nw["urls"]
    proxy: Any = nw["proxy"]
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    results = loop.run_until_complete(agetResponses(urls, proxy))  # type: dict
    loop.run_until_complete(asyncio.sleep(0.25))
    loop.close()
    return results


async def getSesh(url: str, proxy: str, sesh: aiohttp.ClientSession):
    myResponse: str = ""
    try:
        async with sesh.get(url, proxy=proxy) as sresponse:
            myResponse = await sresponse.text()
    except Exception as e:
        myResponse = f"FAILURE: {e}"
    finally:
        return (url, myResponse)


async def agetResponses(urls: list, proxy: str) -> dict:
    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    res = dict()
    conn = aiohttp.TCPConnector(limit=None, limit_per_host=0)
    async with aiohttp.ClientSession(
        connector=conn,
        timeout=aiohttp.ClientTimeout(60.0, 15.0),
        headers=headers,
        connector_owner=False,
    ) as sesh:
        tasks: list = []
        for url in urls:
            if not url or not url.startswith("http"):
                continue
            tasks.append(getSesh(url, proxy, sesh))

        results: list[Any] = await asyncio.gather(*tasks)

        for url, result in results:
            res[url] = result
    conn.close()
    return res


def auditPages(urld: dict, proxy: str = "", mainKeyword: str = "") -> dict:
    urls = list(urld.keys())
    numURL: int = len(urls)
    # dh = getBackSEODataHandler()
    star: float = time.time()
    # dpg.set_value(dh.loader1, 0.3)
    # results = mgetResp(urls, proxy)
    results = dict()
    # dpg.set_value(dh.loader1, 0.9)
    # print(f"Getting multiprocess results: {time.time()-star}")
    # star = time.time()
    # results=getResponses({"urls":urls, "proxy":proxy})
    # print(f"Getting asyncio results: {time.time()-star}")
    myR = list()
    myD = dict()
    with Pool(processes=multiprocessing.cpu_count() - 1) as pool:
        for url, text in results.items():
            myR.append(
                (
                    url,
                    text,
                    mainKeyword,
                    urld[url],
                )
            )
        # dpg.set_value(dh.loader2, 1/len(results))
        myL: list[PageAudit] = pool.starmap(PageAudit, myR)
        # dpg.set_value(dh.loader1, 1.0)
        # dpg.set_value(dh.loader2, 0.0)
        for aud in myL:
            # aud=auds.join()
            myD[aud.url] = aud
    return myD


def getStopWords() -> list[str]:
    return [
        "dr",
        "dra",
        "mr",
        "ms",
        "a",
        "a's",
        "able",
        "about",
        "above",
        "according",
        "accordingly",
        "across",
        "actually",
        "after",
        "afterwards",
        "again",
        "against",
        "ain't",
        "all",
        "allow",
        "allows",
        "almost",
        "alone",
        "along",
        "already",
        "also",
        "although",
        "always",
        "am",
        "among",
        "amongst",
        "an",
        "and",
        "another",
        "any",
        "anybody",
        "anyhow",
        "anyone",
        "anything",
        "anyway",
        "anyways",
        "anywhere",
        "apart",
        "appear",
        "appreciate",
        "appropriate",
        "are",
        "aren't",
        "around",
        "as",
        "aside",
        "ask",
        "asking",
        "associated",
        "at",
        "available",
        "away",
        "awfully",
        "b",
        "be",
        "became",
        "because",
        "become",
        "becomes",
        "becoming",
        "been",
        "before",
        "beforehand",
        "behind",
        "being",
        "believe",
        "below",
        "beside",
        "besides",
        "best",
        "better",
        "between",
        "beyond",
        "both",
        "brief",
        "but",
        "by",
        "c",
        "c'mon",
        "c's",
        "came",
        "can",
        "can't",
        "cannot",
        "cant",
        "cause",
        "causes",
        "certain",
        "certainly",
        "changes",
        "clearly",
        "co",
        "com",
        "come",
        "comes",
        "concerning",
        "consequently",
        "consider",
        "considering",
        "contain",
        "containing",
        "contains",
        "corresponding",
        "could",
        "couldn't",
        "course",
        "currently",
        "d",
        "definitely",
        "described",
        "despite",
        "did",
        "didn't",
        "different",
        "do",
        "does",
        "doesn't",
        "doing",
        "don't",
        "done",
        "down",
        "downwards",
        "during",
        "e",
        "each",
        "edu",
        "eg",
        "eight",
        "either",
        "else",
        "elsewhere",
        "enough",
        "entirely",
        "especially",
        "et",
        "etc",
        "even",
        "ever",
        "every",
        "everybody",
        "everyone",
        "everything",
        "everywhere",
        "ex",
        "exactly",
        "example",
        "except",
        "f",
        "far",
        "few",
        "fifth",
        "first",
        "five",
        "followed",
        "following",
        "follows",
        "for",
        "former",
        "formerly",
        "forth",
        "four",
        "from",
        "further",
        "furthermore",
        "g",
        "get",
        "gets",
        "getting",
        "given",
        "gives",
        "go",
        "goes",
        "going",
        "gone",
        "got",
        "gotten",
        "greetings",
        "h",
        "had",
        "hadn't",
        "happens",
        "hardly",
        "has",
        "hasn't",
        "have",
        "haven't",
        "having",
        "he",
        "he's",
        "hello",
        "help",
        "hence",
        "her",
        "here",
        "here's",
        "hereafter",
        "hereby",
        "herein",
        "hereupon",
        "hers",
        "herself",
        "hi",
        "him",
        "himself",
        "his",
        "hither",
        "hopefully",
        "how",
        "howbeit",
        "however",
        "i",
        "i'd",
        "i'll",
        "i'm",
        "i've",
        "ie",
        "if",
        "ignored",
        "immediate",
        "in",
        "inasmuch",
        "inc",
        "indeed",
        "indicate",
        "indicated",
        "indicates",
        "inner",
        "insofar",
        "instead",
        "into",
        "inward",
        "is",
        "isn't",
        "it",
        "it'd",
        "it'll",
        "it's",
        "its",
        "itself",
        "j",
        "just",
        "k",
        "keep",
        "keeps",
        "kept",
        "know",
        "knows",
        "known",
        "l",
        "last",
        "lately",
        "later",
        "latter",
        "latterly",
        "least",
        "less",
        "lest",
        "let",
        "let's",
        "like",
        "liked",
        "likely",
        "little",
        "look",
        "looking",
        "looks",
        "ltd",
        "m",
        "mainly",
        "many",
        "may",
        "maybe",
        "me",
        "mean",
        "meanwhile",
        "merely",
        "might",
        "more",
        "moreover",
        "most",
        "mostly",
        "much",
        "must",
        "my",
        "myself",
        "n",
        "name",
        "namely",
        "nd",
        "near",
        "nearly",
        "necessary",
        "need",
        "needs",
        "neither",
        "never",
        "nevertheless",
        "new",
        "next",
        "nine",
        "no",
        "nobody",
        "non",
        "none",
        "noone",
        "nor",
        "normally",
        "not",
        "nothing",
        "novel",
        "now",
        "nowhere",
        "o",
        "obviously",
        "of",
        "off",
        "often",
        "oh",
        "ok",
        "okay",
        "old",
        "on",
        "once",
        "one",
        "ones",
        "only",
        "onto",
        "or",
        "other",
        "others",
        "otherwise",
        "ought",
        "our",
        "ours",
        "ourselves",
        "out",
        "outside",
        "over",
        "overall",
        "own",
        "p",
        "particular",
        "particularly",
        "per",
        "perhaps",
        "placed",
        "please",
        "plus",
        "possible",
        "presumably",
        "probably",
        "provides",
        "q",
        "que",
        "quite",
        "qv",
        "r",
        "rather",
        "rd",
        "re",
        "really",
        "reasonably",
        "regarding",
        "regardless",
        "regards",
        "relatively",
        "respectively",
        "right",
        "s",
        "said",
        "same",
        "saw",
        "say",
        "saying",
        "says",
        "second",
        "secondly",
        "see",
        "seeing",
        "seem",
        "seemed",
        "seeming",
        "seems",
        "seen",
        "self",
        "selves",
        "sensible",
        "sent",
        "serious",
        "seriously",
        "seven",
        "several",
        "shall",
        "she",
        "should",
        "shouldn't",
        "since",
        "six",
        "so",
        "some",
        "somebody",
        "somehow",
        "someone",
        "something",
        "sometime",
        "sometimes",
        "somewhat",
        "somewhere",
        "soon",
        "sorry",
        "specified",
        "specify",
        "specifying",
        "still",
        "sub",
        "such",
        "sup",
        "sure",
        "t",
        "t's",
        "take",
        "taken",
        "tell",
        "tends",
        "th",
        "than",
        "thank",
        "thanks",
        "thanx",
        "that",
        "that's",
        "thats",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "thence",
        "there",
        "there's",
        "thereafter",
        "thereby",
        "therefore",
        "therein",
        "theres",
        "thereupon",
        "these",
        "they",
        "they'd",
        "they'll",
        "they're",
        "they've",
        "think",
        "third",
        "this",
        "thorough",
        "thoroughly",
        "those",
        "though",
        "three",
        "through",
        "throughout",
        "thru",
        "thus",
        "to",
        "together",
        "too",
        "took",
        "toward",
        "towards",
        "tried",
        "tries",
        "truly",
        "try",
        "trying",
        "twice",
        "two",
        "u",
        "un",
        "under",
        "unfortunately",
        "unless",
        "unlikely",
        "until",
        "unto",
        "up",
        "upon",
        "us",
        "use",
        "used",
        "useful",
        "uses",
        "using",
        "usually",
        "uucp",
        "v",
        "value",
        "various",
        "very",
        "via",
        "viz",
        "vs",
        "w",
        "want",
        "wants",
        "was",
        "wasn't",
        "way",
        "we",
        "we'd",
        "we'll",
        "we're",
        "we've",
        "welcome",
        "well",
        "went",
        "were",
        "weren't",
        "what",
        "what's",
        "whatever",
        "when",
        "whence",
        "whenever",
        "where",
        "where's",
        "whereafter",
        "whereas",
        "whereby",
        "wherein",
        "whereupon",
        "wherever",
        "whether",
        "which",
        "while",
        "whither",
        "who",
        "who's",
        "whoever",
        "whole",
        "whom",
        "whose",
        "why",
        "will",
        "willing",
        "wish",
        "with",
        "within",
        "without",
        "won't",
        "wonder",
        "would",
        "would",
        "wouldn't",
        "x",
        "y",
        "yes",
        "yet",
        "you",
        "you'd",
        "you'll",
        "you're",
        "you've",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "z",
        "zero",
    ]


def articleToHTML(article: str) -> tuple[str, str]:
    htmlDoc: str = ""
    saveAs = "Article"
    for line in article.split("\n"):
        if line.strip() == "" or not len(line) > 1:
            continue
        if line.lower().count("conclusion"):
            continue
        hType = "p"
        if line.startswith(("h1:", "h2:", "h3:", "h4:", "h5:", "h6:")):
            sL: list[str] = line.split(":", 1)
            hType: str = sL[0]
            header: str = sL[1]
            if hType == "h1":
                saveAs = header
                continue
        # elif not line.strip().endswith(('.','!','?',':',';',)): continue
        elif line[0].isnumeric() and line.count(":") > 0:
            header = f"<b>{line.split(':')[0]}:</b>{line.split(':', 1)[1]}"
        elif line[0] == "-":
            line: str = line.replace("-", ">>", 1)
            if line.count(":") > 0:
                header = f"<b>{line.split(':')[0]}:</b>{line.split(':', 1)[1]}"
            else:
                header = line
        else:
            header = line
        htmlDoc += f"<{hType}>{header}</{hType}>\n"
    saveAs = f"{os.getcwd()}\\output\\htmls\\{cleanFilename(saveAs)}.html"
    count = 0
    while os.path.exists(saveAs):
        count += 1
        s: list[str] = saveAs.split(".html")
        saveAs: str = f"{s[0]}{count}.html"
    with open(saveAs, "w") as f:
        f.write(htmlDoc)
    return saveAs, htmlDoc


def search(
    sender, app_data, userdata
) -> tuple[
    Literal["core"], Any, Literal["search"], tuple[CompareAudit | Literal[False], str]
]:
    keyword, proxy, numResults, ret = userdata
    # print(f"keyword:{keyword}       proxy:{proxy}            numResults:{numResults}   ")
    executor: Pool = getBackSEODataHandler().getPool()
    gRes = GoogleResults(
        executor=executor, query=keyword, numResults=numResults, proxy=proxy
    )
    myC: CompareAudit | Literal[False] = gRes.search()
    fname: Any | str = (
        cleanFilename(keyword).strip().replace("\t", "").replace("\n", "")
    )
    nfname: str = (
        f"output/search_results_audit/{fname}{cleanFilename(str(numResults))}.caudit"
    )
    with open(nfname, "wb") as f:
        pickle.dump(myC, f)
    return ("core", ret, "search", (myC, nfname))


def getResults() -> dict:
    folder_path = "output/results/"
    resultsData = {}
    for filename in os.listdir(folder_path):
        if filename.endswith("results.json"):
            filepath: str = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                searchTerm: str = filename.split("results.jso")[0]
                if len(data):
                    resultsData[searchTerm] = data
    return resultsData


def getCompared() -> dict:
    folder_path = "output/compared/"
    comparedData = {}
    for filename in os.listdir(folder_path):
        if filename.endswith("compared.json"):
            filepath: str = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                searchTerm: str = filename.split("compared.jso")[0]
                if len(data):
                    comparedData[searchTerm] = data
    return comparedData


def getAudit() -> dict:
    folder_path = "output/audit/"
    auditData = dict()
    for filename in os.listdir(folder_path):
        if filename.endswith("audit.json"):
            filepath: str = os.path.join(folder_path, filename)
            with open(filepath, "r") as f:
                data = json.load(f)
                searchTerm: str = filename.split("audit.jso")[0]
                if len(data):
                    auditData[searchTerm] = data
    return auditData


# def get_article_keywords(article: str) -> list:
#     try:
#         myRake = _Rake(
#             include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=0
#         )
#         myRake2 = _Rake(
#             include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=1
#         )
#         myRake3 = _Rake(
#             include_repeated_phrases=False, max_length=7, min_length=2, ranking_metric=2
#         )
#         myL = list()
#         myRake.extract_keywords_from_text(article)
#         myRake2.extract_keywords_from_text(article)
#         myRake3.extract_keywords_from_text(article)
#         myL.extend(myRake.get_ranked_phrases())
#         myL.extend(myRake2.get_ranked_phrases())
#         myL.extend(myRake3.get_ranked_phrases())
#         return list(set(myL))
#     except:
#         return list()


# def get_keyword_count(article: str) -> list:
#     try:
#         article_keywords = get_article_keywords(article=article)
#         keyword_count = list()
#         for keyw in list(set(article_keywords)):
#             if article.lower().count(keyw) > 1:
#                 keyword_count.append((keyw, article.lower().count(keyw)))
#         return keyword_count
#     except:
#         return list()


def load_dpg_img(img_path: str, registry: int | str) -> int | str:
    width, height, channels, data = dpg.load_image(img_path)
    return dpg.add_static_texture(width, height, data, parent=registry)


def sort_callback(sender, sort_specs):
    if sort_specs is None:
        return
    # print(dpg.get_value(sender))
    # print(sort_specs)
    rows = dpg.get_item_children(sender, 1)
    loc = dpg.get_item_children(sender, 0).index(sort_specs[0][0])
    sortable_list = list()
    for row in rows:
        first_cell = dpg.get_item_children(row, 1)[loc]
        # print(dpg.get_value(first_cell))
        sortable_list.append([row, dpg.get_value(first_cell)])

    def _sorter(e):
        # print(e)
        return e[1]

    sortable_list.sort(key=_sorter, reverse=sort_specs[0][1] < 0)
    new_order = list()
    for pair in sortable_list:
        new_order.append(pair[0])
    dpg.reorder_items(sender, 1, new_order)


if __name__ == "__main__":
    # import _GoogleResults
    import pickle

    # myR = _GoogleResults.GoogleResults()
    # res = myR.pullCompetition("nutritional value from eating cats", {"http": "", "https": ""}, 50)

    # myD = auditPages(res) # type: Dict[str, PageAudit]
    import os

    myD = dict()
    for fil in os.listdir("output/search_results_audit"):
        if fil.endswith(".pkl"):
            with open(f"output/search_results_audit/{fil}", "rb") as f:
                myi = pickle.load(f)  # type: PageAudit
            myD[myi.url] = myi
    # for d in myD.values():
    # 	fnam = cleanFilename(d.url).strip().replace("\t","").replace("\n","")
    # 	with open(f"output/search_results_audit/{fnam}.pkl", 'wb') as f:
    # 		pickle.dump(d, f, -1)
    myC: CompareAudit = CompareAudit(myD)
    with open(f"output/search_results_audit/thePick.caud", "w") as f:
        json.dump(myC.json(), f)
    print(myD)
