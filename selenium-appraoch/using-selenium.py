import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import logging
import urllib.parse
import json
from datetime import datetime



logging.basicConfig(
    level=logging.INFO,  # DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("tweets_scraper.log", encoding="utf-8"),  # log to file
        logging.StreamHandler() 
    ]
)
logger = logging.getLogger(__name__)


# --- SQLAlchemy Setup ---
Base = declarative_base()
class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String(255))
    datetime = Column(String(255))
    post = Column(Text)



# SQLite DB
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.path.join("scrapped_tweets", current_time)
os.makedirs(folder_path, exist_ok=True)
db_path = os.path.join(folder_path, "tweets.db")
db_url = f"sqlite:///{os.path.abspath(db_path)}"
engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# counters
tweet_limit = 400
error_threshold = 10


# batch storage
batch = []
batch_size = 10

def download_driver():
    try:
        logger.info(f"driver download start")
        service = Service(EdgeChromiumDriverManager().install())
        logger.info(f"edge driver downloaded")   
        driver = webdriver.Edge(service=service)
        logger.info(f"driver downlaoded")
        return driver
    except Exception as ex:
        # fallback method, load driver from local folder
        logger.info(f"looking for driver in local machine")
        if os.path.isfile("msedgedriver.exe") :
            service = Service("msedgedriver.exe") 
            driver = webdriver.Edge(service=service)
            return driver
        logger.info(f"driver not found")
        return None
    
# --- Selenium driver setup  ---
def setup_driver():
    try:
        logger.info(f"donwlaoding edge driver")
        driver = download_driver()
        if driver == None:
            return driver
        initial_url = "https://x.com/i/flow/login"
        driver.get(initial_url)
        input_conf = input("Hit Enter after logging in : ")

        if os.path.isfile("using-selenium.json"):
            file = open("using-selenium.json", "r")
            data = json.load(file)
            file.close()  # make sure to close it
        else :
            logger.error(f"config file with name using-selenium.json not found")
            return None


        # Pull values
        query = data["query"] if "query" in data else "#nifty"
        logger.info("query : ", query)
        encoded_query = urllib.parse.quote(query)
        driver.get(f"https://x.com/search?q={encoded_query}&src=typed_query&f=live")
        time.sleep(2)
        return driver
    except Exception as ex:
        logger.error(f"Exception while setting up driver {ex} ")
        return None

def scrap_tweets(driver):
    tweet_counter=0
    error_counter = 0
    while tweet_counter <= tweet_limit:
        try:
            element = driver.find_element(By.XPATH, "//div[@aria-label='Timeline: Search timeline']")
            tweet_divs = element.find_elements(By.XPATH, ".//div[@data-testid='cellInnerDiv']")

            logger.info(f"Found {len(tweet_divs)} divs inside timeline")

            for child in tweet_divs:
                try:
                    author = child.find_element(By.XPATH, './/div[@data-testid="User-Name"]').text.strip().split("\n")[1]
                    dt = child.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                    post = child.find_element(By.XPATH, ".//div[@dir='auto']").text.strip()
                    logger.info(f"****** Tweet Count {tweet_counter}******")
                    logger.info(f"author {author}, dt {dt}, post {post}")

                    # check duplicates in current batch
                    if any(t.author == author and t.datetime == dt and t.post == post for t in batch):
                        continue  

                    batch.append(Tweet(author=author, datetime=dt, post=post))
                    tweet_counter += 1

                    # If batch full -> insert into DB
                    if len(batch) >= batch_size:
                        session.add_all(batch)
                        session.commit()
                        logger.info(f"Inserted {len(batch)} tweets into DB ")
                        batch.clear()

                    if tweet_counter >= tweet_limit:
                        break

                except Exception as e:
                    logger.error(f"Skipping tweet, exception: {e}")

            driver.execute_script("window.scrollBy(0, 4000);")
            time.sleep(4)

        except Exception as ex:
            error_counter += 1
            logger.error(f" Excption {ex}, error counter {error_counter}")
            if error_counter >= error_threshold:
                logger.error("error treshold exceeded")
                break

    # Insert any leftover tweets
    if batch:
        session.add_all(batch)
        session.commit()
        logger.info(f"Inserted remaining {len(batch)} tweets into DB (ORM)")

    session.close()
    driver.quit()


if __name__ == "__main__":
    logger.info(f"App started")
    driver = setup_driver()
    if driver != None:
        scrap_tweets( driver )
    logger.info(f"App ended")