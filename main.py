from Scweet.scweet import scrape, ask_user_and_wait, dump_dataframe_to_csv
from Scweet.user import get_user_information, get_users_following, get_users_followers
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import json
from reddit import Reddit
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
# Assuming Scweet class is defined elsewhere and imported

# Constants
SETTINGS_FILE = "settings.json"

# Function to save current form fields to a JSON file

def save_current_fields():
    data = {
        'words': words_entry.get(),
        'since': since_entry.get(),
        'until': until_entry.get(),
        'from_account': from_account_entry.get(),
        'display_type': display_type_combobox.get(),
        'lang': lang_combobox.get(),
        'save_images': save_images_var.get(),
        'filter_replies': filter_replies_var.get(),
        'proximity': proximity_var.get(),
        'headless': headless_var.get()
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f)

# Function to load last inputs from JSON file


def load_last_inputs():
    today = datetime.now()

    # Get yesterday's date
    yesterday = today - timedelta(days=2)

    # Format dates as 'yyyy-mm-dd'
    today_formatted = today.strftime('%Y-%m-%d')
    yesterday_formatted = yesterday.strftime('%Y-%m-%d')
    since_entry.insert(0, yesterday_formatted)
    until_entry.insert(0, today_formatted)
    try:
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return
    try:
        words_entry.insert(0, data.get('words', ''))
        from_account_entry.insert(0, data.get('from_account', ''))
        display_type_combobox.set(data.get('display_type', 'Top'))
        lang_combobox.set(data.get('lang', 'en'))
        save_images_var.set(data.get('save_images', False))
        filter_replies_var.set(data.get('filter_replies', False))
        proximity_var.set(data.get('proximity', False))
        headless_var.set(data.get('headless', True))
    except FileNotFoundError:
        pass

# Function to handle scraping in a separate thread
def init_vars():
    global scweet_object
    save_current_fields()
    words = [word.strip() for word in words_entry.get().split(',')]
    since = since_entry.get()
    until = until_entry.get()
    from_account = from_account_entry.get() if from_account_entry.get() != '' else None
    display_type = display_type_combobox.get().capitalize()
    save_images = save_images_var.get()
    lang = lang_combobox.get()
    filter_replies = filter_replies_var.get()
    proximity = proximity_var.get()
    headless = headless_var.get()
    interval = 1  # Static, as per your example

    # Creating Scweet object with GUI inputs
    scweet_object = scrape(words=words, since=since, until=until, from_account=from_account,
                           interval=interval, headless=headless, display_type=display_type, 
                           save_images=save_images, lang=lang, filter_replies=filter_replies,
                           proximity=proximity)

    threading.Thread(target=perform_scrape, daemon=True).start()
    

def perform_scrape():
    scweet_object.login_sam()
    ask_user_and_wait()
    data = scweet_object.start_scrape()
    dump_dataframe_to_csv(data, "jstlk.csv")
    messagebox.showinfo("Information", "Scraping completed and data saved to jstlk.csv!")

# Mock function, replace with actual implementation
def dump_dataframe_to_csv(data, filename):
    # Assuming 'data' is a pandas DataFrame
    data.to_csv(filename)

# Placeholder for the CAPTCHA handling
def ask_user_and_wait():
    messagebox.showinfo("CAPTCHA", "Please solve the CAPTCHA if needed and click OK to continue.")



if __name__ == "__main__":
    # Setting up the GUI
    root = tk.Tk()
    root.title("Twitter Data Scrape GUI")
        # Get today's date

    # Applying a dark theme
    style = ttk.Style()
    style.theme_use('alt')  # 'clam' supports theme changes
    style.configure('.', background='#999999', foreground='black')
    style.map('TCheckbutton', background=[('selected', '#333'), ('active', '#505050')])
    
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame['borderwidth'] = 2
    frame['relief'] = 'sunken'

    # Input fields
    row_counter = 0
    ttk.Label(frame, text="Words delim(,) ? OR : AND)").grid(
        column=0, row=row_counter, sticky=tk.W)
    words_entry = ttk.Entry(frame, width=50)
    words_entry.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))

    row_counter += 1
    ttk.Label(frame, text="Since (YYYY-MM-DD):").grid(column=0, row=row_counter, sticky=tk.W)
    since_entry = ttk.Entry(frame)
    since_entry.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))

    row_counter += 1
    ttk.Label(frame, text="Until (YYYY-MM-DD):").grid(column=0, row=row_counter, sticky=tk.W)
    until_entry = ttk.Entry(frame)
    until_entry.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))

    row_counter += 1
    ttk.Label(frame, text="From Account:").grid(column=0, row=row_counter, sticky=tk.W)
    from_account_entry = ttk.Entry(frame)
    from_account_entry.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))

    row_counter += 1
    ttk.Label(frame, text="Display Type:").grid(column=0, row=row_counter, sticky=tk.W)
    display_type_combobox = ttk.Combobox(frame, values=["Top", "Latest", "Mixed"], state="readonly")
    display_type_combobox.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))
    display_type_combobox.set("Top")

    row_counter += 1
    save_images_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Save Images", variable=save_images_var).grid(column=0, row=row_counter, sticky=tk.W, columnspan=2)

    row_counter += 1
    lang_combobox = ttk.Combobox(frame, values=["en", "fr", "de", "it", "es"], state="readonly")
    lang_combobox.grid(column=1, row=row_counter, sticky=(tk.W, tk.E))
    ttk.Label(frame, text="Language:").grid(column=0, row=row_counter, sticky=tk.W)
    lang_combobox.set("en")

    row_counter += 1
    filter_replies_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Filter Replies", variable=filter_replies_var).grid(column=0, row=row_counter, sticky=tk.W, columnspan=2)

    row_counter += 1
    proximity_var = tk.BooleanVar()
    ttk.Checkbutton(frame, text="Proximity", variable=proximity_var).grid(column=0, row=row_counter, sticky=tk.W, columnspan=2)

    row_counter += 1
    headless_var = tk.BooleanVar()
    headless_var.set(True)  # Default headless to true for convenience
    ttk.Checkbutton(frame, text="Headless Browser", variable=headless_var).grid(column=0, row=row_counter, sticky=tk.W, columnspan=2)

    # Start button
    row_counter += 1
    scrape_button = ttk.Button(frame, text="Start Scraping", command=init_vars)
    scrape_button.grid(column=0, row=row_counter, columnspan=2, sticky=(tk.W, tk.E))
    load_last_inputs()
    root.mainloop()