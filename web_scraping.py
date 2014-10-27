#!/usr/bin/python

from lxml import html
import requests
import pprint
from myThread import MyThread
import ho.pisa as pisa
import subprocess
import StringIO
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


def HTML2PDF(data, filename, open=False):

    """
        Simple test showing how to create a PDF file from
        PML Source String. Also shows errors and tries to start
        the resulting PDF
    """
    pdf = pisa.CreatePDF(StringIO.StringIO(data), file(filename, "wb"),
                         link_callback=link_callback)
    if open and (not pdf.err):
        subprocess.call(["open", str(filename)])
    return not pdf.err


def link_callback(uri, rel):
    path = "/Users/Ram/Dev/Scraping/Dates/"
    if uri.find(".jpg") > 1:
        print uri.find(".jpg")
        print "calling the call back", uri, rel
        print path+uri
        return path+uri


def main():
    threads = []
    global pages
    page_response = Requests_Html(url)
    tree = html.fromstring(page_response.text)
    page_index = tree.xpath('/html/body//blockquote/p/a/@href')
    pages[url] = page_response
    return

    for index, html_index in enumerate(page_index):
        html_ = base_url + html_index
        t = MyThread(Requests_Html, (html_,), html_)
        threads.append(t)

    for i in threads:
        i.start()

    for j in threads:
        j.join()

    # pages[k] = i.getResult()
    pages = MyThread.getResult()
    pages[url] = page_response
    print pp.pprint(pages)
    # for i in range(page.qsize()):
    #    pages[i] = page.get()


if __name__ == "__main__":
    main()
    print pages[url]
    HTML2PDF(pages[url].text, "test.pdf", open=True)
