# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:51:16 2017

@author: fbardolle
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import os


session = requests.session()
url = 'http://flora/flora/jsp/sso/index_jcifs_sso.jsp'
session.post(url, auth=('', ''))

time.sleep(2)

def url_downloader(url, name, session):
    """
        Download and save a file, given an url.

        :param url: The url of the file to be downloaded
        :type url: str
        :param name: The name (includind extension) of the file to be saved
        :type name: str
        :param session: A Session objet (see http://docs.python-requests.org/en/master/_modules/requests/sessions/)
        :type name: requests.sessions.Session

        :Example:
        url = "http://flora/flora/index_view_direct_anonymous.jsp?success=servlet/PhotoManager?&recordId=default:UNIMARC:395050&idocsId=ged:IDOCS:447593&resolution=LOW"
        name = 'rapport.docx'
        url_downloader(url, name)
    """
    request = session.get(url)
    with open(name, 'wb') as file:
        file.write(request.content)


"""
Codes FLORA pour les différents types de rapport
ROD : 124;116
Communication au Parlement : 205;132
Rapport public annuel : 207
Rapports public (Rapport public thématique + Rapport sur l'exécution des finances ...
publiques  + Rapport sur la sécurité sociale) : 126;127;128;129
Référé : 130
"""

data = {
"TOUS_FC" :"",
"FT_CRIT":"",
"TYPE_DOC" : "124;116;205;132;207;126;127;128;129;130", # Rapports Cour + CRTC
#"TYPE_DOC" : "205;132;207;126;127;128;129;130", # Rapports Cour
"OPER_DATE" : "between",
"DATE1" : "2016",
"DATE2" : "2016",
"query" : "SIMPLE_TI_CEDOC",
"source" : "default",
"table" : "UNIMARC",
"ActionManagerInit" : "true",
"sysFormTagHidden":""
}


headers = {
"Host" : "flora",
"Connection" : "keep-alive",
"Content-Length" : "293",
"Cache-Control" : "max-age=0",
"Origin" : "http://flora",
"Upgrade-Insecure-Requests" : "1",
"Content-Type" : "application/x-www-form-urlencoded",
"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Referer" : "http://flora/flora/jsp/ccjf/search/welcome_page/welcome5.jsp",
"Accept-Encoding" : "gzip, deflate",
"Accept-Language" : "ja-JP,ja;q=0.8,fr-FR;q=0.6,fr;q=0.4,en-US;q=0.2,en;q=0.2,la;q=0.2"
}


def flora_key_extractor(link):
    result = re.search(r'AUNIMARC%3A(.*?)&setCache=default', link)
    if result is not None:
        return(result.group(1))


def get_page_info(flora_key):
    print("Getting info on %s" % (flora_key))
    r = session.get("http://flora/flora/servlet/ViewManager?menu=menu_view&record=default:UNIMARC:" + flora_key +"&setCache=default.UNIMARC&fromList=true")
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', 'TableView')
    link_dict = {}
    if table is not None:
        for link in table.findAll('a'):
            link_dict[link.string] = link['href']

    metadata = pd.read_html(r.text, attrs={'class': 'TableView'})[0]
    metadata = metadata.set_index(0).to_dict()

    return metadata[1], link_dict


def docx_downloader(link_dict, metadata):

    # Create a data folder if it doesn't exist
    directory = "data"
    if not os.path.exists(directory):
        os.makedirs(directory)

    doc_saved = 0
    for name in link_dict:
        if name is not None:
            if name.endswith(".docx"):
                url = link_dict[name]
                if doc_saved == 0:
                    new_name = metadata["Clé Flora"] + ".docx"
                else:
                    new_name = metadata["Clé Flora"] + "-" + str(doc_saved) + ".docx"
                url_downloader(url, directory + "/" + new_name, session)
                doc_saved += 1
                print("Saving file %s as %s from %s" % (name, new_name ,url))
    metadata["Nombre de fichier sauvegardé"] = doc_saved
    return metadata


# Post a request on the server
r2 = session.post("http://flora/flora/servlet/ActionFlowManager?confirm=action_confirm&forward=action_forward&action=search", data = data, headers = headers)
print(r2)
time.sleep(1)

# Get the search page
r3 = session.get("http://flora/flora/jsp/system/search/search_result_exec.jsp?pagerName=search&mode=")
print(r3)
soup = BeautifulSoup(r3.text, 'html.parser')
time.sleep(1)

# TODO: factorize these 3 lines:
search_links = [link.get('href') for link in soup.find_all("a")]
flora_keys = [flora_key_extractor(link) for link in search_links]
flora_keys = [key for key in flora_keys if key is not None]

count_pages = int(soup.find("div", {"id": "queryCountPages"}).text)
print("%s pages de résultats" %(count_pages))

if count_pages > 1:
    for page in range(1, count_pages):
        page_url = "http://flora/flora/jsp/system/search/search_result_exec.jsp?page=" + str(page+1)
        print(page_url)
        # Get the search page
        r_page = session.get(page_url)
        print(r_page)
        soup = BeautifulSoup(r_page.text, 'html.parser')
        time.sleep(1)

        search_links = [link.get('href') for link in soup.find_all("a")]
        current_flora_keys = [flora_key_extractor(link) for link in search_links]
        current_flora_keys = [key for key in current_flora_keys if key is not None]

        flora_keys.extend(current_flora_keys)


metadatas = []
seen_pages = []
for flora_key in flora_keys:
    if flora_key not in seen_pages:
        metadata, link_dict = get_page_info(flora_key)
        metadata = docx_downloader(link_dict, metadata)
        metadatas.append(metadata)
        seen_pages.append(flora_key)


columns = ['Clé Flora', 'Date du document', 'Nombre de fichier sauvegardé',
           'Titre', 'Type document', 'Juridiction', 'Entité Productrice']


pd.DataFrame(metadatas).to_csv("data/metadonnees.csv", sep = ";", na_rep = "NA",
                                index = False, columns = columns)
