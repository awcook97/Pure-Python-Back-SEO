from Utils._Rake import _Rake, Metric
from nltk.tokenize import word_tokenize, TweetTokenizer, PunktTokenizer

def get_article_keywords(article: str) -> list:
    try:
        myRake = _Rake(
            include_repeated_phrases=False,
            max_length=7,
            min_length=2,
            ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO,
            word_tokenizer=TweetTokenizer().tokenize,
        )
        myRake2 = _Rake(
            include_repeated_phrases=False,
            max_length=7,
            min_length=2,
            ranking_metric=Metric.WORD_DEGREE,
            word_tokenizer=word_tokenize
        )
        myRake3 = _Rake(
            include_repeated_phrases=True,
            max_length=7,
            min_length=2,
            ranking_metric=Metric.WORD_FREQUENCY,
            sentence_tokenizer=PunktTokenizer().tokenize,
        )
        myL = list()
        myRake.extract_keywords_from_text(article)
        myRake2.extract_keywords_from_text(article)
        myRake3.extract_keywords_from_text(article)
        myL.extend(myRake.get_ranked_phrases())
        myL.extend(myRake2.get_ranked_phrases())
        myL.extend(myRake3.get_ranked_phrases())
        return list(set(myL))
    except:
        return list()


def get_keyword_count(article: str) -> list:
    try:
        article_keywords = get_article_keywords(article=article)
        keyword_count = list()
        for keyw in list(set(article_keywords)):
            if article.lower().count(keyw) > 1:
                keyword_count.append((keyw, article.lower().count(keyw)))
        return keyword_count
    except:
        return list()