from pygooglenews import GoogleNews
import newspaper
import datetime
import pandas as pd
from llm import llm_create_db_entry


def get_news_websites(search):
    """find urls, given a search term"""
    websites = []
    start_date = datetime.date(2023,6,16)
    end_date = datetime.date(2023,6,17)
    
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
    """get article content as plain text, given an url"""
    try:
        article = newspaper.Article(url=url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error occurred while processing article: {e}")
        return "failed"


def get_website_contents(articles):
    """Enriches an panda df of articles by a content-column, containing the article as plain text.
    If it fails to get the content, it will remove the entry from the df and print an error message"""
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


def _contains_keywords(article, keywords, threshold):
    """checks, whether an article contains at least <threshold> keywords
        article: string
    """
    count = 0
    for keyword in keywords:
        if keyword.lower() in article.lower():
            count += 1
    return count >= threshold


def filter_on_keywords(articles, keywords, threshold):
    """ Enriches an panda df of articles by a passed_keyword_filter-column, stating whether they pass the filter or not. 
    True: contains keywords, filter passed. 
    False: doesn't contain enough keywords, filter not passed."""
    
    keyword_filter = [False for _ in range (0,len(articles))]
    articles['passed_keyword_filter'] = keyword_filter
    passed = 0
    
    for article in articles.itertuples():
        if _contains_keywords(article.content, keywords, threshold):
            articles.at[article.Index, 'passed_keyword_filter'] = True
            passed += 1

    print("  Keyword filtering finished, Passed: {}, Didn't pass: {}".format(passed, len(articles) - passed))
    return 


def scrape_and_save():
    # Search for refugee and get urls of websites containing news articles
    print('Searching for websites...')
    articles = pd.DataFrame(get_news_websites('refugee'))[:5] # only 5 for testing

    # Try to scrape the urls and get the plain article
    print('Scraping websites...')
    get_website_contents(articles)

    # Save the articles to a csv file
    print('Saving articles to csv...')
    articles.to_csv('articles.csv')


def load_articles():
    # Load the articles from the csv file
    print('Loading articles from csv...')
    articles = pd.read_csv('articles.csv')
    return articles


def filter_and_save(articles):
    # Filter the articles on keywords (and later also llm classifier)
    print('Filtering articles on keywords...')
    keywords = ['refugee', 'death', 'accident', 'the']
    threshold = 3
    filter_on_keywords(articles, keywords, threshold)
    articles.to_csv('articles_filtered.csv')


# scrape_and_save()
articles = load_articles()
filter_and_save(articles)
print(llm_create_db_entry(articles.iloc[0]))
