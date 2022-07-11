import time
from selenium.webdriver.common.by import By

from .context import ScraperContext, scraper_context_required

CHAPTERS = {
    'Intro': 'https://app.codesignal.com/arcade/intro',
    'TheCore': 'https://app.codesignal.com/arcade/code-arcade',
    'Databases': 'https://app.codesignal.com/arcade/db',
    'Python': 'https://app.codesignal.com/arcade/python-arcade',
    'Graphs': 'https://app.codesignal.com/arcade/graphs-arcade'
}

@scraper_context_required
def obtain_tasks(link):
    '''
    A function obtains list of tasks in chapter.
    '''
    
    driver = ScraperContext().driver

    driver.get(link)
    time.sleep(5)

    for a in driver.find_elements(By.CLASS_NAME, '-solved'):
        try:
            yield a.find_elements(By.TAG_NAME, 'span')[0].text, a.get_attribute('href')
        except IndexError:
            continue
