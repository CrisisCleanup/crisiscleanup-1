from lettuce import before, after, world
from selenium import webdriver
import lettuce_webdriver.webdriver

@before.all
def setup_browser():
    world.browser = webdriver.Firefox()

@after.all
def shutdown_browser(results):
    world.browser.close()
