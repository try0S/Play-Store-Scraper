import time
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

# URLs for apps and games
# Adding more URLs possible
URLs = ["https://play.google.com/store/apps?gl=DE", "https://play.google.com/store/games?gl=DE"]



def scroll_down(browser):
    SCROLL_PAUSE_TIME = 2
 
    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")
    time.sleep(SCROLL_PAUSE_TIME)
    
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        #Press "show more" button if available
        try:
            show_more = browser.find_element(By.CLASS_NAME, "RveJvd")
            show_more.click()
            time.sleep(SCROLL_PAUSE_TIME)
        except:
            pass

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scroll_right(browser):
    # Get sections
    sections = browser.find_elements(By.CLASS_NAME, "aoJE7e")
    for s in sections:
        # Scroll section into view
        browser.execute_script("arguments[0].scrollIntoView(true);", s)
        # Get scroll width
        scroll_max = browser.execute_script("return arguments[0].scrollLeftMax", s)
        while True:
            # Scroll to the left
            browser.execute_script("arguments[0].scrollLeft = arguments[0].scrollLeftMax", s)
            # Wait to load apps
            time.sleep(1)
            # Calculate new scroll maximum and compare with last scroll maximum
            new_scroll_max = browser.execute_script("return arguments[0].scrollLeftMax", s)
            if new_scroll_max == scroll_max:
                break
            scroll_max = new_scroll_max

def get_app_ids(browser, print_cats, cats=None, limit=0):
    # Get sections
    sections = browser.find_elements(By.TAG_NAME, "section")
    num_sections = 0
    app_ids = []

    for c in sections:
        try:
            # Get name of app category
            cat_name = c.find_element(By.CLASS_NAME, "kcen6d")
            # Get apps in category
            if not cats or cat_name.text in cats:
                apps = c.find_elements(By.CLASS_NAME, "Si6A0c")
                if limit > 0:
                    apps = apps[:limit]
                # Get app IDs
                app_count = 0

                for app in apps:
                    app_id = app.get_attribute("href")
                    app_id = app_id.replace("https://play.google.com/store/apps/details?id=", "")
                    if "€" in app.text:
                        continue
                    app_count+=1
                    app_ids.append(app_id)
                    
                if print_cats:
                    print(f"{cat_name.text :<30}: {app_count}")
                num_sections+=1
        except NoSuchElementException:
            pass
    
    # Remove duplicates
    app_ids = list(dict.fromkeys(app_ids))

    if print_cats:
        print()
        print(f"{'Total categories' :<30}: {num_sections}")
        print(f"{'Total Apps' :<30}: {len(app_ids)}")
        print("-------------------------------------")
        print()
    
    return app_ids

def write_csv(data_list, csv_path):
    f = open(csv_path, 'w')
    writer = csv.writer(f)

    for data in data_list:
        writer.writerow([data])

    f.close()

def main(cats=None, verbose=False, limit=0, csv_path="DataInput.csv"):
    """
        Scrape App IDs from Google Play and write them to a CSV file
        Parameters:
            cats (list): A list of categories to scrape from Google Play. If `None`, it scrapes all categories.
                         Default: `None`
            verbose (boolean): If set to True, the function prints all the App IDs that were scraped. 
                               Default: False
            limit (int): Integer value indicating how many App IDs to write to the CSV file. 
                         Useful for ranking purposes. 
                         If set to 0, writes all the scraped App IDs to the CSV file.
                         Default: 0
            csv_path (string):  A string that indicates the path of the output CSV file. Default: "DataInput.csv"
                                
    """

    firefox_options = Options()
    firefox_options.headless = False
    browser = webdriver.Firefox(options=firefox_options)
    all_app_ids = []
    for url in URLs:
        #Open Page
        browser.get(url)
        #Scroll down to load all sections
        scroll_down(browser)
        #Scroll all sections to the left to load all apps
        scroll_right(browser)
        #Get app IDs
        app_ids = get_app_ids(browser, verbose, cats, limit)
        all_app_ids += app_ids


    print("-------------------------------------")
    print(f"{'Total Apps' :<30}: {len(all_app_ids)}")
    #Create DataInput.csv
    write_csv(all_app_ids, csv_path)


if __name__ == '__main__':
    main()