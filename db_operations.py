from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env file
load_dotenv()
# Parameters for connection
params = {
    'host': os.getenv('PGHOST'),
    'user': os.getenv('PGUSER'),
    'password': os.getenv('PGPASSWORD'),
    'port': os.getenv('PGPORT'),
    'dbname': os.getenv('PGDATABASE')
}

print(params)

def insert_article(article):
    try:
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO articles (title, summary, website, content, keywords, date, number_dead, number_missing, number_survivors, country_of_origin, region_of_origin, cause_of_death, region_of_incident, country_of_incident, location_of_incident, latitude, longitude) 
            VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, 
            (article['title'], article['summary'], article['website'], article['content'], article['keywords'], article['date'], article['number_dead'], article['number_missing'], article['number_survivors'], article['country_of_origin'], article['region_of_origin'], article['cause_of_death'], article['region_of_incident'], article['country_of_incident'], article['location_of_incident'], article['latitude'], article['longitude'])
        )
        conn.commit()
        print("Record inserted successfully")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()
