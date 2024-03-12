import csv
import os
import datetime
import argparse
from time import sleep
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from .utils import init_driver, get_last_date_from_csv, log_search_page, keep_scroling, dowload_images
import tkinter as tk
from tkinter import messagebox, simpledialog


class ScweetStorage:
    def __init__(self, since, until=None, words=None, to_account=None, from_account=None, mention_account=None,
                 interval=5, lang=None, headless=True, limit=float("inf"), display_type="Top", resume=False,
                 proxy=None, hashtag=None, show_images=False, save_images=False, save_dir="outputs",
                 filter_replies=False, proximity=False, geocode=None, minreplies=None, minlikes=None,
                 minretweets=None):

        # Initialize driver inside the class

        self.driver = None
        self.since = since
        self.until = until
        self.words = words
        self.to_account = to_account
        self.from_account = from_account
        self.mention_account = mention_account
        self.interval = interval
        self.lang = lang
        self.headless = headless
        self.limit = limit
        self.display_type = display_type
        self.resume = resume
        self.proxy = proxy
        self.hashtag = hashtag
        self.show_images = show_images
        self.save_images = save_images
        self.save_dir = save_dir
        self.filter_replies = filter_replies
        self.proximity = proximity
        self.geocode = geocode
        self.minreplies = minreplies
        self.minlikes = minlikes
        self.minretweets = minretweets
        self.data = []
        self.header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis',
                       'Comments', 'Likes', 'Retweets', 'Image link', 'Tweet URL']
        self.path = None
        self.write_mode = 'w'
        self.last_scraped_date = None
        self.until_local = None

    def login_sam(self):
        input_field = self.driver.find_element(
            By.CSS_SELECTOR, 'input[autocomplete="username"]')
        input_field.clear()  # Clear any pre-filled text in the input field
        # Replace your_username with the desired value
        input_field.send_keys(os.environ['SCWEET_USERNAME'])
        button_xpath = "//span[contains(text(),'Next')]/ancestor::div[@role='button']"
        button = self.driver.find_element(By.XPATH, button_xpath)

        # Click the button
        button.click()

        sleep(1)
        password_input = self.driver.find_element(
            By.CSS_SELECTOR, 'input[type="password"]')

        # Enter the password into the input field
        password_input.send_keys(os.environ['SCWEET_PASSWORD'])
        button_xpath = "//span[contains(text(),'Log in')]/ancestor::div[@role='button']"
        button = self.driver.find_element(By.XPATH, button_xpath)

        # Click the button
        button.click()
        sleep(1)
        

    def continue_scrape(self):
        with open(self.path, self.write_mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if self.write_mode == 'w':
                # write the csv header
                writer.writerow(self.header)
            # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
                    
            if self.until is None:
                self.until = datetime.date.today().strftime("%Y-%m-%d")
            while self.until_local <= datetime.datetime.strptime(self.until, '%Y-%m-%d'):
                # number of scrolls
                scroll = 0
                # convert <since> and <until_local> to str
                if type(self.since) != str:
                    self.since = datetime.datetime.strftime(
                        self.since, '%Y-%m-%d')
                try:
                    if self.until_local and type(self.until_local) != str:
                        self.until_local = datetime.datetime.strftime(
                            self.until, '%Y-%m-%d')
                except Exception as e:
                    self.until_local = self.until
                # log search page between <since> and <until_local>
                self.path = log_search_page(driver=self.driver, words=self.words, since=self.since,
                                       until_local=self.until_local, to_account=self.to_account,
                                       from_account=self.from_account, mention_account=self.mention_account, hashtag=self.hashtag, lang=self.lang,
                                       display_type=self.display_type, filter_replies=self.filter_replies, proximity=self.proximity,
                                       geocode=self.geocode, minreplies=self.minreplies, minlikes=self.minlikes, minretweets=self.minretweets)
                # number of logged pages (refresh each <interval>)
                self.refresh += 1
                # number of days crossed
                #days_passed = refresh * interval
                # last position of the page : the purpose for this is to know if we reached the end of the page or not so
                # that we refresh for another <since> and <until_local>
                last_position = self.driver.execute_script(
                    "return window.pageYOffset;")
                # Should we keep scrolling?
                scrolling = True
                print("Looking for tweets between " + str(self.since) +
                      " and " + str(self.until_local) + " ...")
                print(" Path : {}".format(self.path))
                # Number of tweets parsed
                tweet_parsed = 0
                # Sleep
                sleep(random.uniform(0.5, 1.5))
                # Start scrolling and get tweets
                driver, self.data, writer, self.tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
                    keep_scroling(self.driver, self.data, writer, self.tweet_ids,
                                  scrolling, tweet_parsed, self.limit, scroll, last_position)

                # Keep updating <start date> and <end date> for every search
                # Updated parsing logic to handle potential datetime strings including time ('00:00:00')
                if not isinstance(self.since, datetime.datetime):
                    try:
                        self.since = datetime.datetime.strptime(
                            self.since, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        self.since = datetime.datetime.strptime(
                            self.since, '%Y-%m-%d')
                self.since += datetime.timedelta(days=self.interval)

                if isinstance(self.until_local, str):
                    try:
                        self.until_local = datetime.datetime.strptime(
                            self.until_local, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        self.until_local = datetime.datetime.strptime(
                            self.until_local, '%Y-%m-%d')
                self.until_local += datetime.timedelta(days=self.interval)

                # If you need to use them as strings later on, convert them back to string format:
                # self.since = self.since.strftime('%Y-%m-%d')
                # self.until_local = self.until_local.strftime('%Y-%m-%d')

        self.data = pd.DataFrame(self.data, columns=['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis',
                                                     'Comments', 'Likes', 'Retweets', 'Image link', 'Tweet URL'])

        # save images
        if self.save_images == True:
            print("Saving images ...")
            save_images_dir = "images"
            if not os.path.exists(save_images_dir):
                os.makedirs(save_images_dir)

            dowload_images(self.data["Image link"], save_images_dir)

        # close the web driver
        driver.close()

        return self.data

    
def scrape(since, until=None, words=None, to_account=None, from_account=None, mention_account=None, interval=5, lang=None,
          headless=True, limit=float("inf"), display_type="Top", resume=False, proxy=None, hashtag=None, 
          show_images=False, save_images=False, save_dir="outputs", filter_replies=False, proximity=False, 
          geocode=None, minreplies=None, minlikes=None, minretweets=None):
    """
    scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
    until it reaches the <until> date if it's given, else it stops at the actual date.

    return:
    data : df containing all tweets scraped with the associated features.
    save a csv file containing all tweets scraped with the associated features.
    """

    # ------------------------- Variables : 
    # header of csv    
    scweet_storage = ScweetStorage(since, until=until, words=words, to_account=to_account, from_account=from_account, mention_account=mention_account, interval=5, lang=None,
                                   headless=headless, limit=float("inf"), display_type=display_type, resume=resume, proxy=proxy, hashtag=hashtag,
                                   show_images=show_images, save_images=save_images, save_dir=save_dir, filter_replies=filter_replies, proximity=proximity,
                                    minreplies=minreplies, minlikes=minlikes, minretweets=minretweets, geocode=geocode)
    scweet_storage.header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes', 'Retweets',
                  'Image link', 'Tweet URL']
    # list that contains all data 
    scweet_storage.data = []
    # unique tweet ids
    scweet_storage.tweet_ids = set()
    # write mode 
    scweet_storage.write_mode = 'w'
    # start scraping from <since> until <until>
    # add the <interval> to <since> to get <until_local> for the first refresh
    scweet_storage.until_local = datetime.datetime.strptime(
        scweet_storage.since, '%Y-%m-%d') + datetime.timedelta(days=interval)
    # if <until>=None, set it to the actual date
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    # set refresh at 0. we refresh the page for each <interval> of time.
    scweet_storage.refresh = 0

    # ------------------------- settings :
    # file path
    if words:
        if type(words) == str: 
            words = words.split("//")
        path = save_dir + "/" + '_'.join(words) + '_' + str(scweet_storage.since).split(' ')[0] + '_' + \
               str(until).split(' ')[0] + '.csv'
    elif from_account:
        path = save_dir + "/" + from_account + '_' + str(scweet_storage.since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    elif to_account:
        path = save_dir + "/" + to_account + '_' + str(scweet_storage.since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    elif mention_account:
        path = save_dir + "/" + mention_account + '_' + str(scweet_storage.init_date).split(' ')[0] + '_' + str(scweet_storage.max_date).split(' ')[
            0] + '.csv'
    elif hashtag:
        path = save_dir + "/" + hashtag + '_' + str(scweet_storage.since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    # create the <save_dir>
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # show images during scraping (for saving purpose)
    if save_images == True:
        show_images = True
    # initiate the driver
    driver = init_driver(headless, proxy, show_images)
    driver.get(r"https://twitter.com/i/flow/login?redirect_after_login=%2Fsearch%3Fq%3D(jstlk)%2520until%253A2021-10-02%2520since%253A2021-10-01%2520lang%253Aen%26src%3Dtyped_query")
    sleep(5)
    
    scweet_storage.path = path
    scweet_storage.driver = driver
    return scweet_storage



def ask_user_and_wait(root, root_temp):
    # Initial Tkinter setup for the first dialog
    
    response = messagebox.askyesno(
        "Question", "Do you want to interact with the Chrome window now?")
    root_temp.destroy()  # Destroy the root after getting the response

    if response:
        # User clicked 'Yes'
        print("User chose to interact. Proceeding to open Chrome for interaction...")
        simpledialog.askstring("Interaction", "Interact with the Chrome window. Close this prompt when finished.", parent=root_temp)

        print("User finished interaction. Proceeding with the script...")
    else:
        # User clicked 'No'
        print("User chose not to interact. Proceeding without interaction.")


def dump_dataframe_to_csv(dataframe, file_path, include_index=False, sep=","):
    """
    Dumps the given pandas DataFrame to a CSV file.
    
    Parameters:
    - dataframe (pd.DataFrame): The DataFrame to dump.
    - file_path (str): The path where the CSV file will be saved.
    - include_index (bool): Whether to include the DataFrame's index in the CSV. Defaults to False.
    - sep (str): The separator to use in the CSV file. Defaults to comma (,).
    """
    try:
        dataframe.to_csv(file_path, index=include_index, sep=sep)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        # It's generally a good idea to catch and handle exceptions
        # that might occur during file writing - e.g., due to permission issues or disk space.
        print(f"Failed to write data to {file_path}: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape tweets.')

    parser.add_argument('--words', type=str,
                        help='Queries. they should be devided by "//" : Cat//Dog.', default=None)
    parser.add_argument('--from_account', type=str,
                        help='Tweets from this account (example : @Tesla).', default=None)
    parser.add_argument('--to_account', type=str,
                        help='Tweets replyed to this account (example : @Tesla).', default=None)
    parser.add_argument('--mention_account', type=str,
                        help='Tweets mention a account (example : @Tesla).', default=None)
    parser.add_argument('--hashtag', type=str, 
                        help='Hashtag', default=None) 
    parser.add_argument('--until', type=str,
                        help='Max date for search query. example : %%Y-%%m-%%d.', required=True)
    parser.add_argument('--since', type=str,
                        help='Start date for search query. example : %%Y-%%m-%%d.', required=True)
    parser.add_argument('--interval', type=int,
                        help='Interval days between each start date and end date for search queries. example : 5.',
                        default=1)
    parser.add_argument('--lang', type=str,
                        help='Tweets language. example : "en" for english and "fr" for french.', default=None)
    parser.add_argument('--headless', type=bool,
                        help='Headless webdrives or not. True or False', default=False)
    parser.add_argument('--limit', type=int,
                        help='Limit tweets per <interval>', default=float("inf"))
    parser.add_argument('--display_type', type=str,
                        help='Display type of twitter page : Latest or Top', default="Top")
    parser.add_argument('--resume', type=bool,
                        help='Resume the last scraping. specify the csv file path.', default=False)
    parser.add_argument('--proxy', type=str,
                        help='Proxy server', default=None)
    parser.add_argument('--proximity', type=bool,
                        help='Proximity', default=False)                        
    parser.add_argument('--geocode', type=str,
                        help='Geographical location coordinates to center the search, radius. No compatible with proximity', default=None)
    parser.add_argument('--minreplies', type=int,
                        help='Min. number of replies to the tweet', default=None)
    parser.add_argument('--minlikes', type=int,
                        help='Min. number of likes to the tweet', default=None)
    parser.add_argument('--minretweets', type=int,
                        help='Min. number of retweets to the tweet', default=None)
                            

    args = parser.parse_args()

    words = args.words
    until = args.until
    since = args.since
    interval = args.interval
    lang = args.lang
    headless = args.headless
    limit = args.limit
    display_type = args.display_type
    from_account = args.from_account
    to_account = args.to_account
    mention_account = args.mention_account
    hashtag = args.hashtag
    resume = args.resume
    proxy = args.proxy
    proximity = args.proximity
    geocode = args.geocode
    minreplies = args.minreplies
    minlikes = args.minlikes
    minretweets = args.minlikes

    data = scrape(since=since, until=until, words=words, to_account=to_account, from_account=from_account, mention_account=mention_account,
                hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
                display_type=display_type, resume=resume, proxy=proxy, filter_replies=False, proximity=proximity,
                geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
