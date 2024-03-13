import requests
from selenium.webdriver.common.by import By
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import bard
from openai import OpenAI
client = OpenAI(api_key="")

class Reddit:
    def __init__(self, driver, subreddits=[]):
        self.driver = driver
        self.subreddits = subreddits
        
    def process(self):
        """# returns a dictionary of links
        links = {subredit: {title: link}}"""
        links = {} 
        for subreddit in self.subreddits:
            self.get_links(subreddit)
            links.update({subreddit: self.enummer(subreddit)})
        return links
        
    def get_links(self, subreddit):
        self.driver.get(
            f'https://old.reddit.com/r/{subreddit}/top/?sort=top&t=day')
        # Find all <h3> tags on the page
        
    def enummer(self, subreddit):
        x = 0
        links = {}
        while x < 1:
            x+=1
            elements = driver.find_elements(By.XPATH, '//*[@data-event-action="title"]')
            
            print(f"Found {len(elements)} elements with data-event-action attribute equal to 'title'.")
            for e in elements:
                print(e.text)
                links.update({e.text: e.get_attribute('href')})
            self.driver.execute_script("window.scrollBy(0, 1000);")
        return links


def get_hashtags(title, string):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": string},
            {"role": "user", "content": title}
        ]
    )
    print(f'{completion.choices[0].message}\ntitle: {title}\n\n')



if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    reddit = Reddit(driver, ["livestreamfail", "drama", "youtubedrama"])
    links = reddit.process()
    for subreddit, linkobj in links.items():
        print(subreddit)
        for title, link in linkobj.items():
            print(f'{title}: {link}')
            get_hashtags(title, string="What hashtags would you use to describe this post?")
