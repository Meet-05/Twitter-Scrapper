import asyncio
import time
import twscrape
import logging
import json
import os

logging.basicConfig(
    level=logging.INFO,  # DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("tweets_scraper.log", encoding="utf-8"),  # log to file
        logging.StreamHandler()  # also log to console
    ]
)
logger = logging.getLogger(__name__)

logger.info("App started.")
async def worker(queue: asyncio.Queue, api: twscrape.API):
    while True:
        query = await queue.get()
        try:
            tweets = await twscrape.gather(api.search(query, limit=2000))
            logger.info(f"{query} - {len(tweets)} - {int(time.time())}")
            for tweet in  tweets :
                tweet.append({
                "username": tweet.user.username,
                "text": tweet.rawContent,
                "date": tweet.date,
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "hashtags": tweet.hashtags if tweet.hashtags else [],
                "mentions": [m.username for m in tweet.mentionedUsers] if tweet.mentionedUsers else []
                    })
        except Exception as e:
            logger.error(f"Error on {query} - {type(e)}")
        finally:
            queue.task_done()


def read_config():
        if os.path.isfile("using_twsscrape.json"):
            file = open("using_twsscrape.json", "r")
            data = json.load(file)
            file.close() 
            return data
        return None
        
async def main():
    api = twscrape.API()
    config = read_config()
    username = config["username"] if  "username" in config  else ""
    password = config["password"] if "password" in config else ""
    query = config["hashtags"]
    if username != "" and password != "":
        await api.pool.add_account(username, password, "", "")
        await api.pool.login_all()
        queries = config["hashtags"].split(",") if "hashtags" in config else ["#nifty"]
        queue = asyncio.Queue()
        workers_count = 2  # limit concurrency here 2 concurrent requests at time
        workers = [asyncio.create_task(worker(queue, api)) for _ in range(workers_count)]
        for q in queries:
            queue.put_nowait(q)

        await queue.join()
        for worker_task in workers:
            worker_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())