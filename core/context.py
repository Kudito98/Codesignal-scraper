import functools, time, copy
from contextlib import ContextDecorator

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

class InactiveContextError(Exception):
    ''' 
    This exception is raised when a function with decorator "scraper_context_require" is called but "ScraperContext"
    is inactive.
    '''
    pass

def scraper_context_required(func):
    '''
    If a function with this decorator is called and "ScraperContext" is inactive then "InactiveContextErroe" is raised.
    '''

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context = ScraperContext._instance
        # If context._counter == 0 that ScraperContext is inactive.  
        if not context or context._counter == 0:
            raise InactiveContextError()
        
        return func(*args, **kwargs)
    
    return wrapper

class ScraperContext(ContextDecorator):
    '''
    ScraperContext is a singleton which contains all data required for scraper package.
    '''

    _instance = None

    def __new__(clazz):
        if not ScraperContext._instance:
            __class__._instance = super(__class__, clazz).__new__(clazz)
            # It helps to avoid multiple initializations.
            __class__._instance._initialized = False

        return __class__._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._counter = 0
        self._driver = None

        self.options = ChromeOptions()
        self.options.add_argument('--user-data-dir=./chrome-data')
        self.options.headless = True

    def _setup_driver(self):
        '''
        This function is called during "ScraperContext" activation.
        '''
        driver = Chrome(options=self.options)
       
        try:
            time.sleep(1)
            driver.get('https://app.codesignal.com/login')

            wait = WebDriverWait(driver, 5)
            wait.until(lambda d: d.current_url == 'https://app.codesignal.com/')

        except TimeoutException:
            driver.quit()

            options = copy.deepcopy(self.options)
            options.headless = False
            driver = Chrome(options=options)

            time.sleep(1)
            driver.get('https://app.codesignal.com/login')

            wait = WebDriverWait(driver, 100)
            wait.until(lambda d: d.current_url == 'https://app.codesignal.com/')
            driver.quit()

            driver = Chrome(options=self.options)

        self._driver = driver

    def __enter__(self):
        if self._counter == 0:
            self._setup_driver()

        self._counter += 1

    def __exit__(self, *ex):
        self._counter -= 1

        if self._counter == 0:
            self._driver.quit()
            self._driver = None

    @property
    @scraper_context_required
    def driver(self):
        return self._driver
