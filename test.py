from pychrome import pychrome

browser = pychrome.Browser("http://127.0.0.1:12345")

test = browser.list_tab()

print(test[0]._kwargs["title"])