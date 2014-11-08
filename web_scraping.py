#!/usr/bin/python
from lxml import html
# from collections import OrderedDict
import lxml.html.clean as cl
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
# url = "http://www.tangowithdjango.com/book17/"
# base_url = "http://www.tangowithdjango.com/book17/"


def Requests_Html(url, stream=False):
    """
        Gets a  url and returns the response object, which contains the
        html,cookies.. etc
    """
    try:
        page_response = requests.get(url, stream=stream)
        return page_response
    except requests.exceptions.ConnectionError:
        print "DNS Failure, Connection refused"
        print "Check your network connection... are you connected to web"
        exit(0)
    except requests.exceptions.Timeout:
        print "Connection timed out"
        exit(0)


def Extract_Href(response_obj):
    """
        Receives the response_obj and extracts only the href element from the
        html page
    """
    # Create a html tree from response_obj.txt
    tree = html.fromstring(response_obj.text)
    # clean the html tree by removeing css and js reference
    cl.clean(tree)
    # Form the complete url for href
    resolved_tree = html.make_links_absolute(tree, base_url)
    # Delete the used tree obj
    del tree
    # Get the href elemenst from html tree, The iterlink() will produce a
    # generator which will yield (html_element,attribute,link,pos)
    link_iter = html.iterlinks(resolved_tree)
    for elem, attrib, link, pos in link_iter:
        if not link.endswith(".jpg"):
            yield link


def HTML2PDF(data, filename, open_=False):

    """
        Simple test showing how to create a PDF file from
        PML Source String. Also shows errors and tries to start
        the resulting PDF
    """
    with open(filename, "wb") as fp:
        # Since create pdf only accepts file like obj as 1st argument we are
        # passing the response.text to stringio constructor which in turn
        # returns a string stream which acts similar to fileobject
        pdf = pisa.CreatePDF(StringIO.StringIO(data), fp,
                             link_callback=link_callback)
    if open_ and (not pdf.err):
        subprocess.call(["open", str(filename)])
    #  print "finished creating ", filename
    return not pdf.err


def link_callback(uri, rel):
    """
        A call back function which is called by pisa when  images are
        encountered  in the html
    """
    if DEBUG:
        print "\n==================================="
        print "linkcallback called"
        print "uri.jpg===>", uri.find(".jpg")
        print "uri.png===>", uri.find(".png")
        print "uri.svg===>", uri.find(".svg")
        print "uri=====>", uri
        print "uri.replace====>", uri.replace("..", "")
        print "===================================\n"
    if uri.find(".jpg") > 1:
        # url_ = base_url + uri
        dir_sep = "/"
        uri_ = uri.replace("..", "")
        url_ = base_url + uri_
        path = tmp_path + dir_sep + uri_
        if DEBUG:
            print "uri ===>", uri
            print "uri_replace ===>", uri_
            print "url_=====>", url_
            print "base_url ====>", base_url
            print "tmp_path", tmp_path
            print "path======>", path
        image_response = Requests_Html(url_, stream=True)
        print image_response
        with open(path, 'wb') as img_file:
            shutil.copyfileobj(image_response.raw, img_file)
        return path


def fixPdf(pdfFile):
    """
        Writes EOF to the End of the file
    """
    try:
        fileOpen = file(pdfFile, "a")
        fileOpen.write("EOF")
        fileOpen.close()
        return "Fixed"
    except Exception, e:
        return "Unable to open file: %s with error: %s" % (pdfFile, str(e))
    # path = "/Users/Ram/Dev/Scraping/"


def joinPDF(pdf_files):
    """
        Joins separte pdf created to a single pdf
    """
    merger = PyPDF2.PdfFileMerger()
    for file in pdf_files:
        with open(file, "rb") as fp:
            merger.append(fileobj=fp)
    merger.write(open("test_out.pdf", "wb"))
    # Cleanup the files
    for file in pdf_files:
        cleanup(file)


def cleanup(path):
    """
    Removes the directory and subdirectories in path specified
    Path - should not  be a symbolic link
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
    else:
        print "Warning : The path {0} specified for removal does not \
            exists".format(path)


def main():
    """
        The Main Execution function
    """
    threads = []
    global pages
    global html_url
    page_response = Requests_Html(url)
    html_url.append(url)

    # Get the response object for all the links
    for index, url_ in enumerate(Extract_Href(page_response)):
        html_url.append(url_)
        t = MyThread(Requests_Html, (url_,), url_)
        threads.append(t)

    for i in threads:
        i.start()

    for j in threads:
        j.join()

    # Copy the results from mythread static dictionary
    pages = MyThread.getResult().copy()
    pages[url] = page_response
    # print pp.pprint(pages)
    if DEBUG:
        print "length of pages ====>", len(pages)
    # Create a dictionary from pages with key as response.object and
    # value as response object, creating the key this way eliminates the
    # duplicates
    d = {value.text: value for (key, value) in pages.iteritems()}
    # Delete the dictionary containing duplicates
    # del(pages)
    unique_urls = [ur.request.url for ur in d.values()]
    if DEBUG:
        print "lenth of dictionary d ====>", len(d)
        pp.pprint(unique_urls)
    # Intersect both html_url and unique_urls
    [html_url.remove(i) for i in html_url[:] if i not in unique_urls]
    # delete the unique_urls
    del(unique_urls)
    if True:
        print "length of html_url ======>", len(html_url)
        pp.pprint(html_url)

    # Start converting the html to pdfs
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

    if DEBUG:
        pp.pprint(pdf_files)
    joinPDF(pdf_files)

    # Cleanuo the temp folders
    cleanup(tmp_path)

if __name__ == "__main__":
    main()
    # HTML2PDF(pages[url].text, "test.pdf", open=True)
    # HTML2PDF(pag, "test.pdf", open=True
