from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType 
from selenium.webdriver.common.keys import Keys

import socket
from os import path, devnull
import subprocess
from .exceptions import SeleniumServerError, BrowserDeathError, NonFormError
from urllib2 import URLError

import pydoc

class _Selenium():
    def __init__(self, server):
        with open(devnull, "w") as fnull:
            self.selenium = subprocess.Popen(["java", "-jar", server],
                stdout=fnull, stderr=fnull)
        import time
        time.sleep(2) # There has to be a better way!

    def kill(self):
        self.selenium.terminate()
        self.selenium.kill()

class Selenate():
    ''' Initiate a Selenate Object which is secretly a selenium object, A proxy
    can be supplied if so desired otherwise will run locally. Also unless 
    specified Selenate will be a firefox browser.'''
    def __init__(self, host="127.0.0.1", server="./selenium-server.jar"):
        try: # check if the selenium server has been started locally
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = sock.connect_ex(("127.0.0.1", 4444)) == 0
        except:
            port = True # Assume it's started if sock errors out

        if server and path.isfile(server) and not port:
            self.selenium = _Selenium(server)

        proxy = Proxy({
            'proxyType': ProxyType.MANUAL,
            'httpProxy': host,
            'ftpProxy': host,
            'sslProxy': host,
            'noProxy': host 
        })
        caps = webdriver.DesiredCapabilities.FIREFOX
        proxy.add_to_capabilities(caps)
        try:
            self.driver = webdriver.Remote(desired_capabilities=caps)
        except URLError:
            raise SeleniumServerError

    ''' Find an element by a variety of locators, using the format
    "type=locator" (ie "id=some_identifier") ''' 
    def find_element_by_locator(self, locator):
        return SelenateElement(self.driver, locator)

    ''' Have the browser go to some url '''
    def get(self, link):
        self.driver.get(link)

    ''' Wait for a locator to be displayed before continuing, or timeout if this
    takes more than timeout seconds '''
    def wait_for(self, locator, timeout=10):
        w = WebDriverWait(self.driver, timeout)
        w.until(lambda driver: 
                self.driver.find_element_by_locator(locator).is_displayed())

    ''' Click on an element identified by locator on the page '''
    def click(self, locator):
        self.find_element_by_locator(locator).click()

    ''' Exit the browser '''
    def quit(self):
        try:
            self.driver.quit()
        except:
            raise BrowserDeathError
        if hasattr(self, "selenium"):
            self.selenium.kill()

class SelenateElement():
    def __init__(self, driver, locator):
        if "=" in locator:
            locator_type = locator[:locator.find("=")].lower()
            locator_value = locator[locator.find("=") + 1:]
        else:
            locator_type = 'css'
            locator_value = locator

        if locator_type == 'class':
            self.element = driver.find_element_by_class_name(locator_value)
        elif locator_type == 'css':
            self.element = driver.find_element_by_css_selector(locator_value)
        elif locator_type == 'id':
            self.element = driver.find_element_by_id(locator_value)
        else:
            raise "Unkown locator type"

    def attribute(self, value):
        return self.element.get_attribute(value)
    
    def click(self):
        self.element.click()

    def css(self, value):
        return self.element.value_of_css_property(value)

    @property
    def displayed(self):
        return self.element.is_displayed()

    @property
    def enabled(self):
        return self.element.is_enabled()

    @property
    def id(self):
        return self.element.id

    @property
    def location(self):
        return self.element.location

    @property
    def scrolled_location(self):
        location = self.element.location_once_scrolled_into_view
        return {"x" : location.get("x"), "y" : location.get("y")}

    @property
    def size(self):
        return self.element.size

    @property
    def selected(self):
        return self.element.is_selected()

    def submit(self):
        try:
            self.element.submit()
        except NoSuchElementException:
            raise NonFormError

    @property
    def tag(self):
        return self.element.tag_name

    @property
    def text(self):
        return self.element.text

    @text.setter
    def text(self, value):
        self.element.send_keys(value)
