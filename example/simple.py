import selenate

if __name__=="__main__":
    driver = selenate.selenate()
    driver.get("https://github.com/wmak/selenate")
    driver.type_to("id=js-command-bar-field", "Hello World")
    driver.quit()