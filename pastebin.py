#!/usr/bin/env python
"""
Pastebin-Crawler scans recent uploads and collects entries matching a
search_list. To easily browse the results, they will be written to
HTML-files: store.html, with index.html containing an index with links.

Copyright (C) 2014 Steffen Sauler

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
"""

import urllib2                              # d/l web pages
import BeautifulSoup                        # parse URLs
import re                                   # to grep URLs
import time                                 # time.sleep()
from time import gmtime, strftime           # time entry
import sys                                  # sys.stdout()

archive_url = "http://pastebin.com/archive"

# Define the maximum length of saved post in characters
# Huge posts tend to be irrelevant.
max_length  = 100000

# Define seconds between each download. If you set this to 0, you
# will be banned by Pastebin. The default has been tested.
wait_secs   = 2

# Define search-words here!
search_list = ['password',
               'credentials'
               'admin',
               'administrator',
               'mysql'
               'leak', 
               'secret',
               'confidential',
               'restricted',
               'passwort',
               'geheim']

# Define excluded words here!
excl_list   = ['video',
               '.mkv',
               '.wmv',
               '.avi',
               '.mp4',
               'error report',
               'system information'
               'debug',         
               'log',
               'log',
               'FAQ'
               'using',         # Filtering source-code
               'import',
               'include',
               'static',
               'array',
               'function',
               'class',
               'define',
               'git',
               '<head>',        # Filtering complete HTML files
               'script',
               'CloudFlare',    # Some people posting CloudFlare errors
               'Technic']       # Dude using Pastebin as error log

class color:
    red     = '\033[31m'
    green   = '\033[92m'
    reset   = '\033[0m'

def download_page(dl_url):
    try:
        response = urllib2.urlopen(dl_url)
        text = response.read()
    except: 
        sys.stdout.write("Skipping %s" % dl_url)
        text = 0
        pass
    return text

def test_for_relevance(content):
    keyword_list = []
    
    if content != 0 and len(content) < max_length:
        for search_word in search_list:
            if search_word in content:
                keyword_list.append(search_word)
            
        # keyword_list returned empty if an excl_word is seen
        if len(excl_list) > 0:
            for excl_word in excl_list:
                if excl_word in content:
                    keyword_list = []
    return keyword_list
    
def ban_check(content):
    if "banned" in content:
        sys.stdout.write(color.red + "(Pastebin might have banned "\
                         "us for too many downloads.)\n" + color.reset)
        sys.stdout.write("(Please check!)\n")

def save_as_file(name, content):
    ban_check(content)
    sys.stdout.write("Testing pastebin.com/%s:" %name)
    keyword_list = test_for_relevance(content)
   
    if len(keyword_list) > 0:
        sys.stdout.write(color.green + "\t match" + color.reset + "\n")
        
        cur_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
       
        index = open("index.html","a")
        index.write("{tm}&nbsp;-&nbsp;<A HREF='store.html/#{nm}'>" \
                    "{nm}</A>&nbsp;-&nbsp;matched: {kw}<br>"\
                      .format(tm = cur_time, nm = name, \
                              ct = content, kw =keyword_list))
        index.close()
        
        store = open("store.html", "a")
        store.write("<A NAME='{nm}'><br><pre>{ct}</pre><br><hr>"\
                    .format(nm=name, ct=content))
        
        store.close()
    else:
        sys.stdout.write(color.red + "\t no match" + color.reset + "\n")
    time.sleep(wait_secs)

def download_all_urls(url_list):
    for url in url_list:
        page = download_page("http://pastebin.com/raw.php?i=%s" % url)
        save_as_file(url, page)

def extract_urls():
    """ Returns the stripped 8 char pastebin-string """
    sys.stdout.write("Extracting archive-URLs:")
    
    request = urllib2.Request(archive_url)
    response = urllib2.urlopen(request)

    soup = BeautifulSoup.BeautifulSoup(response)
    links = soup.findAll('a', href=re.compile('^\/([A-Za-z0-9]{8})'))

    result = []
    for link in links:
        if not 'settings' in link['href']:
            if not 'languages' in link['href']:
                result.append(link['href'].encode('ascii')[1:])
    sys.stdout.write(color.green + "\t success" + color.reset + "\n")
    return result

def main():
    url_list = extract_urls()
    download_all_urls(url_list)

if __name__ == "__main__":
    main()
