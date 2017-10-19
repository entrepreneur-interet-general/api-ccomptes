# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:51:16 2017

@author: seiteta
"""
import requests
import time
import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from credentials import FLORA_LOGIN, FLORA_PASSWORD


def extract_flora_key(link):
    """
        Extract a Flora key from a link
        
        :param link: A link containing a Flora key
        :type link: str
        :return: A Flora key number (if there is one in the link)
        :rtype: str
    
        :Example:
            
        >>> link = "javascript:sysDoAction('menu_view', '/flora/servlet/ViewManager', '_self', 'record=default%3AUNIMARC%3A388634&setCache=default.UNIMARC&fromList=true','')"
        >>> extract_flora_key(link)
        '388634'
    """
    result = re.search(r'AUNIMARC%3A(.*?)&setCache=default', link)
    if result is not None:
        return(result.group(1))   


def get_page_info(flora_key):
    """
        Get metadata and hyperlinks from a Flora page
        
        :param flora_key: A Flora key
        :type flora_key: str
        :returns: A dictionary of metadata and a dictionary of hyperlink
        :rtype: dict, dict
            
        :Example:
            
        >>> metadata, link_dict = get_page_info('388634')
        Getting info on 388634
        >>> metadata
        {'Clé Flora': '388634',
         'Contre-rapporteurs':...
        >>> link_dict
        {'RF_S-2016-0336.docx': 'http://flora/flora/index_view_direct_anonymous.jsp?success=servlet/PhotoManager?&recordId=default:UNIMARC:388634&idocsId=ged:IDOCS:437425&resolution=LOW',...
    """
    print("Getting info on report n°%s" % (flora_key))
    print(20*"—")
    
    request_get_page = session.get("http://flora/flora/servlet/ViewManager?menu=menu_view&record=default:UNIMARC:" + flora_key +"&setCache=default.UNIMARC&fromList=true")
    soup_get_page = BeautifulSoup(request_get_page.text, 'html.parser')
    table = soup_get_page.find('table', 'TableView')
    link_dict = {}
    if table is not None:
        for link in table.findAll('a'):
            link_dict[link.string] = link['href']
        
    metadata = pd.read_html(request_get_page.text, attrs={'class': 'TableView'})[0]
    metadata = metadata.set_index(0).to_dict()  
    
    return metadata[1], link_dict


def download_url(url, name, session):
    """
        Download and save a file, given an url.
        
        :param url: The url of the file to be downloaded
        :type url: str
        :param name: The name (includind extension) of the file to be saved
        :type name: str
        :param session: A Session objet (see http://docs.python-requests.org/en/master/_modules/requests/sessions/) 
        :type name: requests.sessions.Session
        
        :Example:
            
        >>> url = "http://flora/flora/index_view_direct_anonymous.jsp?success=servlet/PhotoManager?&recordId=default:UNIMARC:388634&idocsId=ged:IDOCS:437425&resolution=LOW"
        >>> name = 'rapport.docx'
        >>> session = requests.session()
        >>> url_login = 'http://flora/flora/jsp/sso/index_jcifs_sso.jsp'
        >>> session.post(url_login, auth=(FLORA_LOGIN, FLORA_PASSWORD))
        >>> time.sleep(2)
        >>> download_url(url, name, session)
    """
    request = session.get(url)    
    with open(name, 'wb') as file:
        file.write(request.content)


def download_docx(link_dict, metadata):
    """
        Download every docx files from a Flora page and update metadata with
        the number of files downloaded.
        
        :param link_dict: A dictionary of link
        :type link_dict: dict
        :param metada: A dictionary of metadata
        :type metadata: dict
        :return: A dictionary of metadata with the number of files downloaded
        :rtype: dict
        
        :Example:
        
        >>> link_dict = {'RF_S-2016-0336.docx': 'http://flora/flora/index_view_direct_anonymous.jsp?success=servlet/PhotoManager?&recordId=default:UNIMARC:388634&idocsId=ged:IDOCS:437425&resolution=LOW'}
        >>> metadata = {'Clé Flora': '388634'}
        >>> download_docx(link_dict, metadata)
        Saving file RF_S-2016-0336.docx as 388634.docx from http://flora/flora/index_view_direct_anonymous.jsp?success=servlet/PhotoManager?&recordId=default:UNIMARC:388634&idocsId=ged:IDOCS:437425&resolution=LOW
        {'Clé Flora': '388634', 'Nombre de fichier sauvegardé': 1}
    """
    
    # Create a data folder if it doesn't exist
    directory = "data"
    if not os.path.exists(directory):
        os.makedirs(directory)
     
    # Download every docx files and rename them
    doc_saved = 0
    for name in link_dict:
        if name is not None:
            if name.endswith(".docx"):
                url = link_dict[name]
                if doc_saved == 0:
                    new_name = metadata["Clé Flora"] + ".docx"
                else:
                    new_name = metadata["Clé Flora"] + "-" + str(doc_saved) + ".docx"
                download_url(url, directory + "/" + new_name, session)
                doc_saved += 1
                print("Saving file %s as %s from %s" % (name, new_name ,url))
                print(20*"—")
                
    # Update the metadata with the number of files downloaded
    metadata["Nombre de fichier sauvegardé"] = doc_saved

    return metadata


# These are the different types of report and their corresponding number in DocJF
#==============================================================================
# ROD : 124;116
# Communication au Parlement : 205;132
# Rapport public annuel 207
# Rapport public ( Rapport public thématique + 
# Rapport sur l'exécution des finances publiques  +
# Rapport sur la sécurité sociale : 126;127;128;129
# Référé : 130
#==============================================================================

data = {
"TOUS_FC" :"",
"FT_CRIT":"",
"TYPE_DOC" : "130",
# "TYPE_DOC" : "124;116;205;132;207;126;127;128;129;130", # Cour + CRTC
#"TYPE_DOC" : "205;132;207;126;127;128;129;130", # Seulement la Cour
"OPER_DATE" : "between",
"DATE1" : "01/01/2016", # Dates can be year (YYYY) or date (dd/mm/yyyy)
"DATE2" : "01/02/2016",
"query" : "SIMPLE_TI_CEDOC",
"source" : "default",
"table" : "UNIMARC",
"ActionManagerInit" : "true",
"sysFormTagHidden":""
}


# Create a session and connect to the service
session = requests.session()
url_login = 'http://flora/flora/jsp/sso/index_jcifs_sso.jsp'
session.post(url_login, auth=(FLORA_LOGIN, FLORA_PASSWORD))
time.sleep(2)
    
# Post a search request
url_search = "http://flora/flora/servlet/ActionFlowManager?confirm=action_confirm&forward=action_forward&action=search"
request_post_search = session.post(url_search, data = data)
print("Post search request status: " + str(request_post_search.status_code))
print(20*"—")
time.sleep(1)
# For more info about the search request:
#soup_post_search = BeautifulSoup(request_post_search.text, 'html.parser')
#print(soup_post_search.prettify())

# Get the first search result page
url_first_search_result_page = "http://flora/flora/jsp/system/search/search_result_exec.jsp?pagerName=search&mode="
request_get_first_search_result_page = session.get(url_first_search_result_page)
print("Get search result request status: " + str(request_get_first_search_result_page.status_code))
print(20*"—")
soup_first_search_result_page = BeautifulSoup(request_get_first_search_result_page.text, 'html.parser')
time.sleep(1)
# For more info about the search result:
#print(soup_first_search_result_page.prettify()

# Count the number of search result page(s)
page_counter = int(soup_first_search_result_page.find("div", {"id": "queryCountPages"}).text)
print("%s result page(s)" %(page_counter))
print(20*"—")

# Create empty dictionaries
flora_keys = []
metadata_list = []
seen_pages = []

# Browse every search result page
for page_number in range(0, page_counter):
    # Get the 'page_number' search result page
    url_search_result_page = "http://flora/flora/jsp/system/search/search_result_exec.jsp?page=" + str(page_number + 1)
    request_get_search_result_page = session.get(url_search_result_page)
    print("Get search result request status: " + str(request_get_search_result_page.status_code))
    print(20*"—")
    soup_search_result_page = BeautifulSoup(request_get_search_result_page.text, 'html.parser')
    time.sleep(1)
    
    # Find all links and extract their Flora key
    search_links = [link.get('href') for link in soup_search_result_page.find_all("a")]
    current_flora_keys = [extract_flora_key(link) for link in search_links]
    current_flora_keys = [key for key in current_flora_keys if key is not None]
    flora_keys.extend(current_flora_keys)

# Browse every report page
for flora_key in flora_keys:
    if flora_key not in seen_pages:
        # Get info on current report page
        metadata, link_dict = get_page_info(flora_key)       
        
        # Download docx files from current report page
        metadata = download_docx(link_dict, metadata)
        
        # Add metadata from current report page
        metadata_list.append(metadata)
        
        # Add Flora key to track which page has been seen
        seen_pages.append(flora_key)

# Keep only some metadata
columns = ['Clé Flora', 'Date du document', 'Nombre de fichier sauvegardé',
           'Titre', 'Type document', 'Juridiction']
# Export metadata to csv
pd.DataFrame(metadata_list).to_csv("data/metadonnees.csv", sep = ";", na_rep = "NA",
                                index = False, columns = columns)