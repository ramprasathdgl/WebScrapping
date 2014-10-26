#!/usr/bin/python

from lxml import html
import requests
import pprint
from myThread import MyThread
# from Queue import Queue

pages = {}
pp = pprint.PrettyPrinter(indent=4)
base_url = "http://www.fao.org/docrep/006/y4360e/"
url = "http://www.fao.org/docrep/006/y4360e/y4360e00.HTM"


def Requests_Html(url):
    try:
        page_response = requests.get(url)
        return page_response
    except requests.exceptions.ConnectionError:
        print "DNS Failure, Connection refused"
        print "Check your network connection... are you connected to web"
        exit(0)


def main():
    threads = []
    page_response = Requests_Html(url)
    tree = html.fromstring(page_response.text)
    page_index = tree.xpath('/html/body//blockquote/p/a/@href')

    for index, html_index in enumerate(page_index):
        html_ = base_url + html_index
        t = MyThread(Requests_Html, (html_,), html_)
        threads.append(t)

    for i in threads:
        i.start()

    for j in threads:
        j.join()

    # pages[k] = i.getResult()
    page = MyThread.getResult()
    print page.qsize()
    for i in range(page.qsize()):
        pages[i] = page.get()


if __name__ == "__main__":
    main()
