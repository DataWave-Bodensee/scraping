from pygooglenews import GoogleNews
import newspaper
import datetime
import pandas as pd
from llm import llm_create_db_entry
from db_operations import insert_article


def _get_news_websites(search):
    """find urls to a given search term
        search: string"""
    websites = []
    start_date = datetime.date(2023,3,1)
    end_date = datetime.date(2023,3,2)
    
    gn = GoogleNews()
    search = gn.search(search, from_=start_date.strftime('%Y-%m-%d'), to_=end_date.strftime('%Y-%m-%d'))
    newsitem = search['entries']

    for item in newsitem:
        website = {
            'title':item.title,
            'link':item.link,
            'published':item.published,
        }
        websites.append(website)

    print("  Found {} websites".format(len(websites)))
    return websites


def _get_website_content(url):
    """Given a single link to an article on a news-website, get the article content as plain text.
    Returns content as plain text or "failed" if it fails to get the content.
        url: string
        return: string
    """
    try:
        article = newspaper.Article(url=url)
        article.download()
        article.parse()
        return article.text if article.text else "failed"
    except Exception as e:
        print(f"Error occurred while processing article: {e}")
        return "failed"


def _get_websites_contents(articles):
    """Enriches the articles panda-df by a content-column, containing the article as plain text.
    If it fails to get the content, it will remove the entry from the df and print an error message.
    articles: panda df"""
    contents = ["" for _ in range (0,len(articles))]
    articles["content"] = contents
    successes = 0
    failures = 0

    for article in articles.itertuples():
        print("  Scraping ", article.link, "...")
        
        content = _get_website_content(article.link)
        
        if content == "failed":
            articles.drop(article.Index, inplace=True)
            failures += 1
        
        else:
            articles.at[article.Index, 'content'] = content
            successes += 1
    
    print("Scraping finished, successfully: {}, failed: {}".format(successes, failures))
    return


def _contains_keywords(article, keywords):
    """checks, which keywords an article contains
        article: string
        return: list of keywords contained in the article
    """
    article_keywords = []
    for keyword in keywords:
        if keyword.lower() in article.lower():
           article_keywords.append(keyword)
    return article_keywords


def scrape():
    """Scrape news websites for articles containing the word 'migration accident'"""
    # Search for refugee and get urls of websites containing news articles
    print('Searching for websites...')
    articles = pd.DataFrame(_get_news_websites('migration accident'))[:50] # 20 for testing

    # Try to scrape the urls and get the plain article
    print('Scraping websites...')
    _get_websites_contents(articles)

    return articles


def filter_on_keywords(articles):
    """ Enriches an panda df of articles by a passed_keyword_filter-column, stating whether they pass the filter or not. 
    True: contains keywords, filter passed. 
    False: doesn't contain enough keywords, filter not passed."""
    
    # Filter the articles on keywords
    print('Filtering articles on keywords...')
    keywords = ['Refugee', 'Death', 'Migrant', 'Missing', ' Body', 'Crossing', 'Asylum', 'Seeker', 'Accident', 'Boat', 'Rescue']
    threshold = 5

    articles['passed_keyword_filter'] = [False for _ in range (0,len(articles))]
    articles['keywords'] = [[] for _ in range (0,len(articles))]

    passed = 0
    
    for article in articles.itertuples():
        contained_keywords = _contains_keywords(article.content, keywords)
        if len(contained_keywords) >= threshold:
            articles.at[article.Index, 'passed_keyword_filter'] = True
            articles.at[article.Index, 'keywords'] = contained_keywords
            passed += 1

    print("  Keyword filtering finished, Passed: {}, Didn't pass: {}".format(passed, len(articles) - passed))
    articles = articles[articles['passed_keyword_filter']]
    return articles


def filter_on_llm_and_extract(articles):
    """Filters the articles on the LLMs assessment and returns array of db-entries"""
    print('Filtering articles on llm...')
    processed_articles = []
    for idx, article in enumerate(articles.itertuples(),1):
        print("Filtering on llm, article {} from {}...".format(idx, len(articles)))
        entry = llm_create_db_entry(article)
        if entry is not None:
            processed_articles.append(entry)
    
    processed_articles = pd.DataFrame(processed_articles)
    print("Finished filtering on llm and extracting data, Filter passed: {}, Didn't pass: {}".format(len(processed_articles), len(articles) - len(processed_articles)))

    return processed_articles


def write_to_db(articles):
    """Write the db-entries to the database"""
    print('Writing articles to the database...')
    for article in articles.itertuples():
        article_dict = article._asdict()
        insert_article(article_dict)
    return


def scrape_filter_write():
    """Main function to scrape, filter and write to the database"""
    articles = scrape()
    articles = filter_on_keywords(articles)
    articles = filter_on_llm_and_extract(articles)
    write_to_db(articles)

scrape_filter_write()
