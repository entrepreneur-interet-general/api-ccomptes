#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:53:09 2017

@author: seiteta
"""
import pandas as pd
import numpy as np
import docx
import re
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

#==============================================================================
# def doc_to_txt(filename):
#     '''
#         Get the path of a Word document and returns the text of this document
# 
#         :param filename: The filename of the doc or docx document
#         :type filename: str
#         :return: The text of the document
#         :rtype: str
# 
#         :Example:
# 
#         >>> doc_to_txt("/Users/seiteta/Work/quen-dit-la-cour/reports/jf00097342.doc")
#         'This is text from a .doc document'
#         >>> doc_to_txt("/Users/seiteta/Work/quen-dit-la-cour/reports/jf00136930.docx")
#         'This is text from a .docx document'
# 
#     '''
#     full_text = []
# 
#     if filename.lower().endswith(".doc"):
#         print("Converting to txt the doc file:" + filename)
#         cmd = ['antiword', filename]
#         p = Popen(cmd, stdout=PIPE)
#         stdout, stderr = p.communicate()
#         full_text = stdout.decode()
# 
#     elif filename.lower().endswith(".docx"):
#         print("Converting to txt the docx file:" + filename)
#         doc = docx.Document(filename)
#         for para in doc.paragraphs:
#             full_text.append(para.text)
#         full_text = '\n'.join(full_text)
# 
#     else :
#         print("Document extension should be either .doc or .docx")
# 
#     return full_text
#==============================================================================


def clean_text(text):
     '''
         Get a text and returns a cleaned text

         :param text: The dirty text
         :type text: str
         :return: The clean text
         :rtype: str

         :Examples:
         >>> clean_text('This text have lots of\n\n\n')
         'This text have lots of   '
         >>> clean_text('<div>This text have HTML</div>')
         'This text have HTML'
         >>> clean_text('This text have too much      spaces')
         'This text have too much spaces'
         >>> clean_text('Ce texte a des mots inutiles')
         'texte mots inutiles'
     '''
     # Replace new lines with spaces
     new_text = text.replace("\n", " ")

     # Remove HTML tags
     start = "<"
     end = ">"
     pattern = '%s(.*?)%s' % (re.escape(start), re.escape(end))
     new_text = re.sub(pattern, '', new_text)

     # Remove extra whitespace
     new_text = ' '.join(new_text.split())
     
     # Remove stop words
     stopwords = ["à", "a", "alors", "au", "aux", "aucuns", "aussi", "autre",
                  "avant", "avec", "avoir", "avez","bon", "ça", "car", "ce",
                  "cela", "ces", "cette", "ceux", "chaque", "ci", "comme",
                  "comment", "dans", "de", "des", "du", "dedans", "dehors",
                  "depuis", "devrait", "doit", "donc", "dos", "début", "elle",
                  "elles", "en", "encore", "étaient", "étions", "étant"
                  "été", "être", "est", "et", "eu", "fait", "faites", "fois",
                  "font", "hors", "ici", "il", "ils", "je", "juste",
                  "la", "le", "les", "leur", "lors", "là" ,"ma", "maintenant",
                  "mais", "mes", "moins", "mon", "même", "ne", "ni",
                  "notre", "nous", "ou", "où", "ont","par", "parce",
                  "pas", "peut", "peu", "plupart", "pour", "pourquoi", "qu",
                  "quand", "que", "quel", "quelle", "quelles", "quels", "qui",
                  "sa", "sans", "ses", "se", "seulement", "si", "sien", "son",
                  "sont", "soyez", "sujet", "sur", "ta", "tandis",
                  "tellement", "tels", "tes", "ton", "tous", "tout", "trop",
                  "très", "tu", "un", "une", "voient", "vont", "votre", "vous",
                  "vu"]
     new_text = ' '.join([word for word in new_text.split() if word.lower() not in stopwords])

     return new_text


def clean_title(text):
     '''
         Get a text and returns a cleaned text

         :param text: The dirty text
         :type text: str
         :return: The clean text
         :rtype: str

         :Example:
         >>> clean_title('This text have [brackets]')
         'This text have '
     '''
     new_text = re.sub('\[.*?\]', '', text)
     return new_text


def list_files(path):
    '''
        Get a path and return a list of all the non-hidden files in this path

        :param path: The path of the directory
        :type path: str
        :return: The list of all the non-hidden files
        :rtype: list

        :Example:
        >>> list_files('/usr/bin')
        ['nscurl',
         'nslookup',
         'nsupdate',
         ...
        ]
    '''
    files_list = [f for f in listdir(path) if isfile(join(path, f)) and not f.startswith('.')]

    return files_list


def remove_html_head(filename):
    '''
        Read an HTML file and remove the <head> part

        :param filename: The name of the HTML file (including path)
        :type filename: str
        :return: A text containing the HTML without the <head>
        :rtype: str

        :Example:
        >>> remove_html_head(path+report_filenames[0])
        '<div><div class="table-grid">\n    <p>\n     <table class="table"> ...'

    '''
    with open(filename, 'r') as html:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.prettify()[631:-18] # These numbers work for HTML files created with my doc_to_HTML program
        text = "<div>" + text

    return text

path = "data/"
#path = "/Users/seiteta/Desktop/dossier sans titre/datasession/2 – Données clef USB/donnees_jf/rapports_publics_2016/"

# Create a list of files
report_filenames = list_files(path)

# Keep only the files ending in .html
report_filenames = [filename for filename in report_filenames if filename.endswith('.html')]

# Create a list containg the text without the <head>
report_txt = [remove_html_head(path + filename) for filename in report_filenames]

# Load this list in a pandas DataFrame
corpus = pd.DataFrame(data = report_txt, index = report_filenames, columns = ["report"])

# Load metadata associated with the file
meta = pd.read_csv(path + "metadonnees.csv", encoding ='ISO-8859-1', sep = ";")
corpus['Clé Flora'] = corpus.index
corpus['Clé Flora'] = corpus['Clé Flora'].apply(lambda x: int(x[:6]))
corpus = corpus.merge(meta, on = 'Clé Flora')

# Generate a DataFrame
cour = pd.DataFrame (data = np.arange(len(corpus)), columns = ["Numéro de dossier"])
cour["Juridiction"] = corpus["Juridiction"] + " (" + corpus["Entité Productrice"] + ")"
cour["Juridiction"] = cour["Juridiction"].apply(lambda x : x.capitalize())
cour["Type"] = corpus["Type document"]
cour["Année"] = corpus["Date du document"].apply(lambda x:x[6:])
cour["Publication"] = corpus["Date du document"]
cour["Objet"] = corpus["Titre"].apply(lambda x:clean_title(x))
cour["Thème et sous thème"] = "N/A"
cour["Mots clés"] = "N/A"
cour['Rapport'] = corpus["report"].values

# Shorten reports for Elasticsearch
cour['Texte index'] = cour['Rapport'].apply(lambda x: clean_text(x)[:30000])


# Export to csv
cour.to_csv("cour.csv", index = None)


# This commented part can be used to automatically generate keywords for each report
#==============================================================================
# # Automatically generate keywords with Tf-Idf
# from sklearn.feature_extraction.text import TfidfVectorizer
#
# french = ["alors", "au", "aux", "aucuns", "aussi", "autre", "avant", "avec", "avoir",
#          "bon", "car", "ce", "cela", "ces", "cette", "ceux", "chaque", "ci", "comme",
#          "comment", "dans", "de", "des", "du", "dedans", "dehors", "depuis", "devrait",
#          "doit", "donc", "dos", "début", "elle", "elles", "en", "encore", "essai",
#          "est", "et", "eu", "fait", "faites", "fois", "font", "hors", "ici", "il",
#          "ils", "je", "juste", "la", "le", "les", "leur", "là", "ma", "maintenant",
#          "mais", "mes", "mine", "moins", "mon", "mot", "même", "ni", "nommés",
#          "notre", "nous", "ou", "où", "ont","par", "parce", "pas", "peut", "peu", "plupart",
#          "pour", "pourquoi", "qu","quand", "que", "quel", "quelle", "quelles", "quels",
#          "qui", "sa", "sans", "ses", "seulement", "si", "sien", "son", "sont",
#          "sous", "soyez", "sujet", "sur", "ta", "tandis", "tellement", "tels",
#          "tes", "ton", "tous", "tout", "trop", "très", "tu", "un", "une", "voient", "vont",
#          "votre", "vous", "vu", "ça", "étaient", "état", "étions", "été", "être",
#          "class", "div", "dsn", "jdc", "td", "tr", "sup", "normal", "toc", "table",
#          "saisie", "texte", "deux", "trois", "quatre", "18", "2001", "2015", "2016", "2017",
#          "madame", "mesdames" , "présidente", "présidentes", "président","monsieur", "ministre",
#          ]
#
# def find_best_phrase(id_report = 0, num_phrases = 10):
#     """
#         Find phrases with the highest tf-idf value
#         Parameters:
#         id_report => ID of a report (integer)
#         num_phrases => Number of phrases to find (integer)
#     """
#
#     # Train the model
#     tf = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df = 0, stop_words = french)
#
#     # Execute the model against our corpus
#     tfidf_matrix =  tf.fit_transform(cour['Rapport'].apply(lambda x: clean_text(x)))
#     feature_names = tf.get_feature_names()
#
#     # Build a dense matrix because some operations can't be done on sparse matrix
#     dense = tfidf_matrix.todense()
#
#     # Select the id_report report
#     report = dense[id_report].tolist()[0]
#
#     # Match feature index with real words
#     phrase_scores = [pair for pair in zip(range(0, len(report)), report) if pair[1] > 0]
#     sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
#
#     # Save num_phrases phrases in a dictionnary
#     best_phrases = {}
#     for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores][:num_phrases]:
#         best_phrases[phrase] = score
#
#     return best_phrases
#
#
# def get_keywords(document, corpus):
#     best_phrases = find_best_phrase(i, 5)
#     list_best_phrases = list(best_phrases.keys())
#     list_best_phrases = ', '.join(list_best_phrases)
#
#     return list_best_phrases
#
# for i in range(len(cour)):
#     cour["Mots clés"].iloc[i] = get_keywords(i, corpus)
#==============================================================================


# Export to csv
cour.to_csv("cour.csv", index = None)
