#!/usr/bin/python
from lxml import html
import requests
import pprint
from myThread import MyThread
import ho.pisa as pisa
import subprocess
import StringIO
import shutil
import tempfile
import os
import PyPDF2

DEBUG = True
pages = {}
html_url = []
pp = pprint.PrettyPrinter(indent=4)
tmp_path = tempfile.mkdtemp()
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
    except requests.exceptions.Timeout:
        print "Connection timed out"
        exit(0)


def HTML2PDF(data, filename, open_=False):

    """
        Simple test showing how to create a PDF file from
        PML Source String. Also shows errors and tries to start
        the resulting PDF
    """
    with open(filename, "wb") as fp:
        pdf = pisa.CreatePDF(StringIO.StringIO(data), fp,
                             link_callback=link_callback)
    if open_ and (not pdf.err):
        subprocess.call(["open", str(filename)])
    print "finished creating ", filename
    return not pdf.err


def link_callback(uri, rel):
    # path = "/Users/Ram/Dev/Scraping/"
    if uri.find(".jpg") > 1:
        # url_ = base_url + uri
        url_ = os.path.join(base_url, uri)
        image_response = requests.get(url_, stream=True)
        with open(os.path.join(tmp_path, uri), 'wb') as img_file:
            shutil.copyfileobj(image_response.raw, img_file)
        del image_response
        if False:
            print "calling the call back", uri, rel
            print os.path.join(tmp_path, uri)
        return os.path.join(tmp_path, uri)


def fixPdf(pdfFile):
    try:
        fileOpen = file(pdfFile, "a")
        fileOpen.write("EOF")
        fileOpen.close()
        return "Fixed"
    except Exception, e:
        return "Unable to open file: %s with error: %s" % (pdfFile, str(e))


def joinPDF(pdf_files):
    merger = PyPDF2.PdfFileMerger()
    for file in pdf_files:
        with open(file, "rb") as fp:
            merger.append(fileobj=fp)
    merger.write(open("test_out.pdf", "wb"))


def main():
    threads = []
    global pages
    global html_url
    page_response = Requests_Html(url)
    tree = html.fromstring(page_response.text)
    page_index = tree.xpath('/html/body/p/b/a/@href')
    # pp.pprint(page_index)
    pages[url] = page_response
    html_url.append(url)

    for index, html_index in enumerate(page_index):
        html_ = base_url + html_index
        html_url.append(html_)
        t = MyThread(Requests_Html, (html_,), html_)
        threads.append(t)

    for i in threads:
        i.start()

    for j in threads:
        j.join()

    pages = MyThread.getResult().copy()
    pages[url] = page_response
    print pp.pprint(pages)
    print pp.pprint(html_url)
    threads = []
    pdf_files = []
    pag = ""
    for j, i in enumerate(html_url):
        pag = pages[i].text
        fn = "{0}test.pdf".format(j)
        pdf_files.append(fn)
        t = MyThread(HTML2PDF, (pag, fn,), fn)
        threads.append(t)
    for th in threads:
        th.start()

    for th in threads:
        th.join()
    pp.pprint(pdf_files)
    joinPDF(pdf_files)

if __name__ == "__main__":
    main()
    # HTML2PDF(pages[url].text, "test.pdf", open=True)
    # HTML2PDF(pag, "test.pdf", open=True)
