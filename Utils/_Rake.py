# -*- coding: utf-8 -*-
"""Implementation of Rapid Automatic Keyword Extraction algorithm.

As described in the paper `Automatic keyword extraction from individual
documents` by Stuart Rose, Dave Engel, Nick Cramer and Wendy Cowley.
"""

import string
from collections import Counter, defaultdict
from enum import Enum
from itertools import chain, groupby, product
from typing import Callable, DefaultDict, Dict, List, Optional, Set, Tuple

import nltk
import nltk.downloader
import nltk.tokenize

nltk.download("punkt_tab")


def init_Rake(name):
    try:
        suffix = b"_" + name.encode("ascii")
    except UnicodeEncodeError:
        suffix = b"U_" + name.encode("punycode").replace(b"-", b"_")
    return b"PyInit" + suffix


# Readability type definitions.
Word = str
Sentence = str
Phrase = Tuple[str, ...]


class Metric(Enum):
    """Different metrics that can be used for ranking."""

    DEGREE_TO_FREQUENCY_RATIO = 0  # Uses d(w)/f(w) as the metric
    WORD_DEGREE = 1  # Uses d(w) alone as the metric
    WORD_FREQUENCY = 2  # Uses f(w) alone as the metric


class _Rake:
    """Rapid Automatic Keyword Extraction Algorithm."""

    def __init__(
        self,
        stopwords: Optional[Set[str]] = None,
        punctuations: Optional[Set[str]] = None,
        language: str = "english",
        ranking_metric: Metric = Metric.DEGREE_TO_FREQUENCY_RATIO,
        max_length: int = 100000,
        min_length: int = 1,
        include_repeated_phrases: bool = True,
        sentence_tokenizer: Optional[Callable[[str], List[str]]] = None,
        word_tokenizer: Optional[Callable[[str], List[str]]] = None,
    ):
        """Constructor.

        :param stopwords: Words to be ignored for keyword extraction.
        :param punctuations: Punctuations to be ignored for keyword extraction.
        :param language: Language to be used for stopwords.
        :param max_length: Maximum limit on the number of words in a phrase
                           (Inclusive. Defaults to 100000)
        :param min_length: Minimum limit on the number of words in a phrase
                           (Inclusive. Defaults to 1)
        :param include_repeated_phrases: If phrases repeat in phrase list consider
                            them as is without dropping any phrases for future
                            calculations. (Defaults to True) Ex: "Magic systems is
                            a company. Magic systems was founded by Raul".

                            If repeated phrases are allowed phrase list would be
                            [
                                (magic, systems), (company,), (magic, systems),
                                (founded,), (raul,)
                            ]

                            If they aren't allowed phrase list would be
                            [
                                (magic, systems), (company,),
                                (founded,), (raul,)
                            ]
        :param sentence_tokenizer: Tokenizer used to tokenize the text string into sentences.
        :param word_tokenizer: Tokenizer used to tokenize the sentence string into words.
        """
        # By default use degree to frequency ratio as the metric.
        if isinstance(ranking_metric, Metric):
            self.metric = ranking_metric
        else:
            self.metric = Metric.DEGREE_TO_FREQUENCY_RATIO

        # If stopwords not provided we use language stopwords by default.
        self.stopwords: Set[str]
        if stopwords:
            self.stopwords = stopwords
        else:
            self.stopwords = {
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
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "0",
            }

        # If punctuations are not provided we ignore all punctuation symbols.
        self.punctuations: Set[str]
        if punctuations:
            self.punctuations = punctuations
        else:
            self.punctuations = set(string.punctuation)

        # All things which act as sentence breaks during keyword extraction.
        self.to_ignore: Set[str] = set(chain(self.stopwords, self.punctuations))

        # Assign min or max length to the attributes
        self.min_length: int = min_length
        self.max_length: int = max_length

        # Whether we should include repeated phreases in the computation or not.
        self.include_repeated_phrases: bool = include_repeated_phrases

        # Tokenizers.
        self.sentence_tokenizer: Callable[[str], List[str]]
        if sentence_tokenizer:
            self.sentence_tokenizer = sentence_tokenizer
        else:
            self.sentence_tokenizer = nltk.tokenize.sent_tokenize  # type: ignore
        self.word_tokenizer: Callable[[str], List[str]]
        if word_tokenizer:
            self.word_tokenizer = word_tokenizer
        else:
            self.word_tokenizer = nltk.tokenize.TweetTokenizer().tokenize

        # Stuff to be extracted from the provided text.
        self.frequency_dist: Dict[Word, int]
        self.degree: Dict[Word, int]
        self.rank_list: List[Tuple[float, Sentence]]
        self.ranked_phrases: List[Sentence]

    def extract_keywords_from_text(self, text: str):
        """Method to extract keywords from the text provided.

        :param text: Text to extract keywords from, provided as a string.
        """
        sentences: List[Sentence] = self._tokenize_text_to_sentences(text)
        self.extract_keywords_from_sentences(sentences)

    def extract_keywords_from_sentences(self, sentences: List[Sentence]):
        """Method to extract keywords from the list of sentences provided.

        :param sentences: Text to extraxt keywords from, provided as a list
                          of strings, where each string is a sentence.
        """
        phrase_list: List[Phrase] = self._generate_phrases(sentences)
        self._build_frequency_dist(phrase_list)
        self._build_word_co_occurance_graph(phrase_list)
        self._build_ranklist(phrase_list)

    def get_ranked_phrases(self) -> List[Sentence]:
        """Method to fetch ranked keyword strings.

        :return: List of strings where each string represents an extracted
                 keyword string.
        """
        return self.ranked_phrases

    def get_ranked_phrases_with_scores(self) -> List[Tuple[float, Sentence]]:
        """Method to fetch ranked keyword strings along with their scores.

        :return: List of tuples where each tuple is formed of an extracted
                 keyword string and its score. Ex: (5.68, 'Four Scoures')
        """
        return self.rank_list

    def get_word_frequency_distribution(self) -> Dict[Word, int]:
        """Method to fetch the word frequency distribution in the given text.

        :return: Dictionary (defaultdict) of the format `word -> frequency`.
        """
        return self.frequency_dist

    def get_word_degrees(self) -> Dict[Word, int]:
        """Method to fetch the degree of words in the given text. Degree can be
        defined as sum of co-occurances of the word with other words in the
        given text.

        :return: Dictionary (defaultdict) of the format `word -> degree`.
        """
        return self.degree

    def _tokenize_text_to_sentences(self, text: str) -> List[Sentence]:
        """Tokenizes the given text string into sentences using the configured
        sentence tokenizer. Configuration uses `nltk.tokenize.sent_tokenize`
        by default.

        :param text: String text to tokenize into sentences.
        :return: List of sentences as per the tokenizer used.
        """
        return self.sentence_tokenizer(text)

    def _tokenize_sentence_to_words(self, sentence: Sentence) -> List[Word]:
        """Tokenizes the given sentence string into words using the configured
        word tokenizer. Configuration uses `nltk.tokenize.wordpunct_tokenize`
        by default.

        :param sentence: String sentence to tokenize into words.
        :return: List of words as per the tokenizer used.
        """
        return self.word_tokenizer(sentence)

    def _build_frequency_dist(self, phrase_list: List[Phrase]) -> None:
        """Builds frequency distribution of the words in the given body of text.

        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        self.frequency_dist = Counter(chain.from_iterable(phrase_list))

    def _build_word_co_occurance_graph(self, phrase_list: List[Phrase]) -> None:
        """Builds the co-occurance graph of words in the given body of text to
        compute degree of each word.

        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        co_occurance_graph: DefaultDict[Word, DefaultDict[Word, int]] = defaultdict(
            lambda: defaultdict(lambda: 0)
        )
        for phrase in phrase_list:
            # For each phrase in the phrase list, count co-occurances of the
            # word with other words in the phrase.
            #
            # Note: Keep the co-occurances graph as is, to help facilitate its
            # use in other creative ways if required later.
            for word, coword in product(phrase, phrase):
                co_occurance_graph[word][coword] += 1
        self.degree = defaultdict(lambda: 0)
        for key in co_occurance_graph:
            self.degree[key] = sum(co_occurance_graph[key].values())

    def _build_ranklist(self, phrase_list: List[Phrase]):
        """Method to rank each contender phrase using the formula

              phrase_score = sum of scores of words in the phrase.
              word_score = d(w) or f(w) or d(w)/f(w) where d is degree
                           and f is frequency.

        :param phrase_list: List of List of strings where each sublist is a
                            collection of words which form a contender phrase.
        """
        self.rank_list = []
        for phrase in phrase_list:
            rank = 0.0
            for word in phrase:
                if self.metric == Metric.DEGREE_TO_FREQUENCY_RATIO:
                    rank += 1.0 * self.degree[word] / self.frequency_dist[word]
                elif self.metric == Metric.WORD_DEGREE:
                    rank += 1.0 * self.degree[word]
                else:
                    rank += 1.0 * self.frequency_dist[word]
            self.rank_list.append((rank, " ".join(phrase)))
        self.rank_list.sort(reverse=True)
        self.ranked_phrases = [ph[1] for ph in self.rank_list]

    def _generate_phrases(self, sentences: List[Sentence]) -> List[Phrase]:
        """Method to generate contender phrases given the sentences of the text
        document.

        :param sentences: List of strings where each string represents a
                          sentence which forms the text.
        :return: Set of string tuples where each tuple is a collection
                 of words forming a contender phrase.
        """
        phrase_list: List[Phrase] = []
        # Create contender phrases from sentences.
        for sentence in sentences:
            word_list: List[Word] = [
                word.lower() for word in self._tokenize_sentence_to_words(sentence)
            ]
            phrase_list.extend(self._get_phrase_list_from_words(word_list))

        # Based on user's choice to include or not include repeated phrases
        # we compute the phrase list and return it. If not including repeated
        # phrases, we only include the first occurance of the phrase and drop
        # the rest.
        if not self.include_repeated_phrases:
            unique_phrase_tracker: Set[Phrase] = set()
            non_repeated_phrase_list: List[Phrase] = []
            for phrase in phrase_list:
                if phrase not in unique_phrase_tracker:
                    unique_phrase_tracker.add(phrase)
                    non_repeated_phrase_list.append(phrase)
            return non_repeated_phrase_list

        return phrase_list

    def _get_phrase_list_from_words(self, word_list: List[Word]) -> List[Phrase]:
        """Method to create contender phrases from the list of words that form
        a sentence by dropping stopwords and punctuations and grouping the left
        words into phrases. Only phrases in the given length range (both limits
        inclusive) would be considered to build co-occurrence matrix. Ex:

        Sentence: Red apples, are good in flavour.
        List of words: ['red', 'apples', ",", 'are', 'good', 'in', 'flavour']
        List after dropping punctuations and stopwords.
        List of words: ['red', 'apples', *, *, good, *, 'flavour']
        List of phrases: [('red', 'apples'), ('good',), ('flavour',)]

        List of phrases with a correct length:
        For the range [1, 2]: [('red', 'apples'), ('good',), ('flavour',)]
        For the range [1, 1]: [('good',), ('flavour',)]
        For the range [2, 2]: [('red', 'apples')]

        :param word_list: List of words which form a sentence when joined in
                          the same order.
        :return: List of contender phrases honouring phrase length requirements
                 that are formed after dropping stopwords and punctuations.
        """
        groups = groupby(word_list, lambda x: x not in self.to_ignore)
        phrases: List[Phrase] = [tuple(group[1]) for group in groups if group[0]]
        return list(
            filter(lambda x: self.min_length <= len(x) <= self.max_length, phrases)
        )


if __name__ == "__main__":
    # import unicodedata
    myP = list(string.punctuation)
    myP.extend(list(string.digits))
    # print(myP)
    myP.append("“")
    myP.append("’")
    myP.append("-")
    myP.append("”")
    myP.append("—")

    myRake = _Rake(
        include_repeated_phrases=False,
        max_length=7,
        min_length=2,
        ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO,
        word_tokenizer=nltk.tokenize.TweetTokenizer().tokenize,
    )
    myRake2 = _Rake(
        include_repeated_phrases=False,
        max_length=7,
        min_length=2,
        ranking_metric=Metric.WORD_DEGREE,
        word_tokenizer=nltk.tokenize.word_tokenize,
    )
    myRake3 = _Rake(
        stopwords=["_"],
        include_repeated_phrases=True,
        punctuations=set(nltk.tokenize.PunktSentenceTokenizer.PUNCTUATION),
        max_length=7,
        min_length=2,
        ranking_metric=Metric.WORD_FREQUENCY,
        sentence_tokenizer=nltk.tokenize.PunktTokenizer().tokenize,
    )
    # print(myRake.get_word_degrees())
    myT = """An Introduction to SEO Basics
		What is SEO? At its core, the meaning of search engine optimization (SEO) is increasing your website’s visibility in the organic search results of major search engines.

		To get that visibility, you must understand three core components:

		What types of content search engine users and your customers want or need.
		How search engines work to discover, index, and serve content in search engine results pages.
		How to properly promote and optimize your website to tell search engines more about it.
		While search engines and technology are always evolving, there are some underlying foundational elements that have remained unchanged from the earliest days of SEO.

		This is why, in collaboration with some of the field’s top authorities and experts, we created these in-depth overviews and tutorials – to define SEO for aspiring SEO professionals and explain how search engine optimization really works now.

		How does SEO work? SEO is a fast-paced and dynamic field. It can also sometimes be frustrating, especially if you’re relying on outdated tactics that no longer work.

		That’s why it’s crucial for you to stay well-informed and learn continuously. Search engines are always updating their algorithms to provide quality search results to their users.

		Artificial intelligence is constantly improving algorithms to ensure better user experiences. Meaning SEO is also more complex than ever today.

		Marketers must continue their SEO education to keep up with what tactics works now, and what tactics need to be removed from your search marketing plan.

		It takes more than just building links, creating any old content, and adding a few keywords to improve your organic search rankings and increase the visibility of your business or brand.

		You need to keep track of and understand:

		Emerging trends (e.g., voice search)
		New features in search related products and tools (e.g., Search Console)
		Technological advancements (e.g., machine learning).
		Your audience (e.g., how they behave and what they want).
		So how do you develop an SEO strategy to dominate your competition in Google and other search engines?

		Because, ultimately, SEO isn’t only about being found on search engines and driving traffic to your website. It’s about providing a great experience and generating leads and revenue.

		To create a positive user experience and generate leads from search, you have to do more than target the right keywords. You have to understand the intent of the search user and develop content that provides solutions for their problems.

		Once you understand your searcher’s intent, you will be able to create content that meets the needs of search users and is optimized for search engines to discover and index it.

		FAQ
		What is SEO?
		SEO stands for search engine optimization, the process by which marketers attempt to get more visibility for their website in search engine results pages on Google, Bing, Yahoo, DuckDuckGo, and other search engines.

		How does SEO work?
		Through the use of technical, on-page, and off page SEO tactics, marketers effectively tell search engines what their website is about and why it should rank well in search engine results pages."""
    myRake.extract_keywords_from_text(myT)
    myRake2.extract_keywords_from_text(myT)
    myRake3.extract_keywords_from_text(myT)
    myDTF = myRake.get_ranked_phrases_with_scores()
    myWD = myRake2.get_ranked_phrases_with_scores()
    myWF = myRake3.get_ranked_phrases_with_scores()
    # print(myRake.get_word_frequency_distribution())

    mynewRake = _Rake(
        include_repeated_phrases=True, ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO, sentence_tokenizer=nltk.tokenize.PunktTokenizer().tokenize,
    )
    mynewRake.extract_keywords_from_text(myT)
    for i in range(int(len(myDTF)/2)):
        print(f"{i}DTF {myDTF[i]} --- WD {myWD[i]} ---- WF {myWF[i]}")
    print(mynewRake.get_ranked_phrases_with_scores()[:10])
