# Twitter-Scrapper
Scraps Tweets based on interests.


This project aims to scrap tweets based on the hashtags feed to the app. Twitter recommends to use it's offical tweepy API, but it is paid. I tried to create a scrapper for my own use. 
There are a few approaches I tried, using a few libraries, but all were down, below are 2 approaches that show some ray of hope. Wanted to add more features like data visualization, and text to signal conversion, but couldn't because of the time constrain. 


1. using selenium and web automation :
Approach - the websited is loaded with in the driver with the help of selenium, we scrap the data from the web page itself. Currently it fetches the author, the time it was posted, and the actual post.


Setup and Running the project :
    - To run this, navigate to selenium-approach.
    - refer the packages used in the project in the requirements. file and install them.
    - It uses msedgedriver for scrapping, donwload the edge driver matching to your edge browser version and place it in the same folder.
    - put your hashtags in  selenium.json, not comma seperated, but the way you query in the actual twitter webste, you can refere the example in the file.
    - run the command python using-selenium.py
    - login to your twitter account.
    - hit enter in the console, once you have logged in.
    - data will be logged in scrapped_tweets\currentdatetime\tweets.db 
    - you can check for logs in tweets_scrapper.log

2. using twsscrap ( Experimental ) :
    - To run this, navigate to selenium-approach.
    - refer the packages used in the project in the requirements. file and install them.
	- enter your credentials in using_twsscrape.json file.
	- enter the coma seperated hash tags.
	- execute the command python ( using_twsscrape.py ), this was not working because I got rate limited and later banned, so test with a throw-away account.
	
	
Below are the other approaches I tried for scrapping.

1. tweepy -
	Tweepy is twitter's offical API, and has a strong support to read raltime and historical data, but it is paid, it has a free tier which is very limited.
2. snscrape -
	Tried to use this library, but it seems that currently ( 10th Sept 2025 ), it is blocked by twitter, I get blocked (404) when I run this.
3. twscrape -
	This libray requires user credentials, which is fine, but it cloudfare blocks the requests.
4. Burp Suite -
	Burp Suite is an security testing tool, which can be used to capture the to and fro traffic, using this traffic we can pickup pieces of data and try to get our work done, wanted to explore this more, but couldn't because of the time constrain.
5. selenium and web automation -
	Use selenium and scrap the data from the webpage, work, but it is slow and fragile.
	
Future Scope :
Perform Text-to-Signal Conversion and signal aggregation ( Couldn't do because of the time constrain and time spent in the approaches in data scrapping ).
