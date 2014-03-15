from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys

class Selenate():
    ''' Initiate a Selenate Object which is secretly a selenium object, A proxy
    can be supplied if so desired otherwise will run locally. Also unless 
    specified Selenate will be a firefox browser.'''
    def __init__(self, host="127.0.0.1"):
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': host,
                'ftpProxy': host,
                'sslProxy': host,
                'noProxy': host 
            })
            caps = webdriver.DesiredCapabilities.FIREFOX
            proxy.add_to_capabilities(caps)
            self.driver = webdriver.Remote(desired_capabilities=caps)

    ''' find an element by a variety of locators, using the format
    "type=locator" (ie "id=some_identifier") ''' 
    def find_element_by_locator(self, locator):
        locator_type = locator[:locator.find("=")].lower()
        locator_value = locator[locator.find("=") + 1:]
        if locator_type == 'class':
            return self.driver.find_element_by_class_name(locator_value)
        elif locator_type == 'css':
            return self.driver.find_element_by_css_selector(locator_value)
        elif locator_type == 'id':
            return self.driver.find_element_by_id(locator_value)
        else:
            return "Unkown locator type"

    ''' have the browser go to some url '''
    def get(self, link):
        self.driver.get(link)

    ''' wait for a locator to be displayed before continuing, or timeout if this
    takes more than timeout seconds '''
    def wait_for(self, locator, timeout=10):
        w = WebDriverWait(self.driver, timeout)
        w.until(lambda driver: self.driver.find_element_by_locator(locator).is_displayed())

    ''' click on an element identified by locator on the page '''
    def click(self, locator):
        self.find_element_by_locator(locator).click()

    ''' type text into a locator '''
    def type_to(self, locator, text):
        self.find_element_by_locator(locator).send_keys(text)

    ''' exit the browser '''
    def quit(self):
        try:
            self.driver.quit()
        except:
            print "force quitted"
