from Scweet.scweet import scrape, ask_user_and_wait, dump_dataframe_to_csv
from Scweet.user import get_user_information, get_users_following, get_users_followers
import tkinter as tk
from dotenv import load_dotenv
import os 

load_dotenv()

# leave as none if set in .env
USERNAME = None
PASSWORD = None

def main():
    os.environ['SCWEET_USERNAME'] = os.environ.get(
        'SCWEET_USERNAME', '') or USERNAME

    os.environ['SCWEET_PASSWORD'] = os.environ.get(
        'SCWEET_PASSWORD', '') or PASSWORD

    scweet_storage = scrape(words=['jstlk'], since="2024-01-01", until="2024-03-01", 
                from_account=None, interval=1, headless=False, display_type="Top", 
                save_images=False, lang="en", filter_replies=False, proximity=False)
    
    scweet_storage.login_sam()
    # ask_user_and_wait() this is for future cases where captcha may be an issue, allow the script to pause for user input. 
    data = scweet_storage.continue_scrape()

    dump_dataframe_to_csv(data, "jstlk.csv")
    # scrape top tweets of with the hashtag #covid19, in proximity and without replies. the process is slower as the
    # interval is smaller (choose an interval that can divide the period of time betwee, start and max date)
    scweet_storage = scrape(hashtag="bitcoin", since="2021-08-05", until="2021-08-08", from_account=None, interval=1,
                headless=True, display_type="Top", save_images=False,
                resume=False, filter_replies=True, proximity=True)

    scweet_storage.login_sam()
    data = scweet_storage.continue_scrape(scweet_storage)
    # Get the main information of a given list of users
    # These users belongs to my following. 

    users = ['nagouzil', '@yassineaitjeddi', 'TahaAlamIdrissi',
            '@Nabila_Gl', 'geceeekusuu', '@pabu232', '@av_ahmet', '@x_born_to_die_x']

    # this function return a list that contains : 
    # ["nb of following","nb of followers", "join date", "birthdate", "location", "website", "description"]

    users_info = get_user_information(users, headless=True)

    # Get followers and following of a given list of users Enter your username and password in .env file. I recommande
    # you dont use your main account. Increase wait argument to avoid banning your account and maximise the crawling
    # process if the internet is slow. I used 1 and it's safe.

    # set your .env file with SCWEET_EMAIL, SCWEET_USERNAME and SCWEET_PASSWORD variables and provide its path
    env_path = ".env"

    following = get_users_following(users=users, env=env_path, verbose=0, headless=True, wait=2, limit=50, file_path=None)

    followers = get_users_followers(users=users, env=env_path, verbose=0, headless=True, wait=1, limit=50, file_path=None)

if __name__ == "__main__":
    # root = tk.Tk()
    # root.withdraw()
    # root.mainloop()
    main()
