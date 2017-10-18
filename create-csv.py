#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:53:09 2017

@author: seiteta
"""
import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join


def clean_text(text):
     '''
         Get a text and returns a cleaned text

         :param text: The dirty text
         :type text: str
         :return: The clean text
         :rtype: str

         :Examples:
         >>> clean_text('<div class="pg1">\n    <p>\n     Le\n    </p>\n   </div>')
         '<div class="pg1">\n    <p>    </p>\n   </div>'
     '''
     if type(text) is str:
         # Remove paragraphs that contain just the word "Le"
         start = "\n"
         end = "Le\n"
         pattern = '%s(.*?)%s' % (re.escape(start), re.escape(end))
         new_text = re.sub(pattern, "", text)
         
         # Remove spurious Windows character
         new_text = text.replace("\x92", "’")
         
         return new_text
     else:
         return text


def simplify_text(text):
     '''
         Get a text and returns a simplified text

         :param text: The complicated text
         :type text: str
         :return: The simplified text
         :rtype: str

         :Examples:
         >>> simplify_text('This text have lots of\n\n\n')
         'This text have lots of   '
         >>> simplify_text('<div>This text have HTML</div>')
         'This text have HTML'
         >>> simplify_text('This text have too much      spaces')
         'This text have too much spaces'
         >>> simplify_text('Ce texte a des mots inutiles')
         'texte mots inutiles'
     '''               
     # Replace new lines with spaces
     new_text = text.replace("\n", " ")

     # Remove HTML tags
     start = "<"
     end = ">"
     pattern = '%s(.*?)%s' % (re.escape(start), re.escape(end))
     new_text = re.sub(pattern, "", new_text)

     # Remove extra whitespace
     new_text = ' '.join(new_text.split())

     # Remove stop words
     stopwords = [u"à", u"a", u"alors", u"au", u"aux", u"aucuns", u"aussi", u"autre",
                  u"avant", u"avec", u"avoir", u"avez", u"bon", u"ça", u"car", u"ce",
                  u"cela", u"ces", u"cette", u"ceux", u"chaque", u"ci", u"comme",
                  u"comment", u"dans", u"de", u"des", u"du", u"dedans", u"dehors",
                  u"depuis", u"devrait", u"doit", u"donc", u"dos", u"début", u"elle",
                  u"elles", u"en", u"encore", u"étaient", u"étions", u"étant"
                  u"été", u"être", u"est", u"et", u"eu", u"fait", u"faites", u"fois",
                  u"font", u"hors", u"ici", u"il", u"ils", u"je", u"juste",
                  u"la", u"le", u"les", u"leur", u"lors", u"là" ,"ma", u"maintenant",
                  u"mais", u"mes", u"moins", u"mon", u"même", u"ne", u"ni",
                  u"notre", u"nous", u"ou", u"où", u"ont","par", u"parce",
                  u"pas", u"peut", u"peu", u"plupart", u"pour", u"pourquoi", u"qu",
                  u"quand", u"que", u"quel", u"quelle", u"quelles", u"quels", u"qui",
                  u"sa", u"sans", u"ses", u"se", u"seulement", u"si", u"sien", u"son",
                  u"sont", u"soyez", u"sujet", u"sur", u"ta", u"tandis",
                  u"tellement", u"tels", u"tes", u"ton", u"tous", u"tout", u"trop",
                  u"très", u"tu", u"un", u"une", u"voient", u"vont", u"votre", u"vous",
                  u"vu"]
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
        text = soup.prettify()[593:-18] # These numbers work for HTML files created with my doc_to_HTML program (use [631:-18] for python3)
        text = "<div>" + text

    return text

# Specify data path
path = "data/"

# Create a list of files
report_filenames = list_files(path)

# Keep only the files ending in .html
report_filenames = [filename for filename in report_filenames if filename.endswith('.html')]

# Create a list containg the text without the <head>
report_txt = [remove_html_head(path + filename) for filename in report_filenames]

# Load this list in a pandas DataFrame
corpus = pd.DataFrame(data = report_txt, index = report_filenames, columns = [u"report"])

# Load metadata associated with the file
meta = pd.read_csv(path + "metadonnees.csv", encoding ='ISO-8859-1', sep = ";")
corpus[u"Clé Flora"] = corpus.index
corpus[u"Clé Flora"] = corpus[u"Clé Flora"].apply(lambda x: int(x[:6]))
corpus = corpus.merge(meta, on = u"Clé Flora")

# Generate a DataFrame
cour = pd.DataFrame (data = np.arange(len(corpus)), columns = [u"Numéro de dossier"])
cour[u"Juridiction"] = corpus[u"Juridiction"] + " (" + corpus[u"Entité Productrice"] + ")"
cour[u"Juridiction"] = cour[u"Juridiction"].apply(lambda x : x.capitalize())
cour[u"Type"] = corpus[u"Type document"]
cour[u"Année"] = corpus[u"Date du document"].apply(lambda x:x[6:])
cour[u"Publication"] = corpus[u"Date du document"]
cour[u"Objet"] = corpus[u"Titre"].apply(lambda x:clean_title(x))
cour[u"Thème et sous thème"] = u"N/A"
cour[u"Mots clés"] = u"N/A"
cour[u"Rapport"] = corpus[u"report"].values    
cour = cour.applymap(clean_text)

# Shorten reports for Elasticsearch
cour[u"Texte index"] = cour[u"Rapport"].apply(lambda x: simplify_text(x)[:30000])


# Export to csv
cour.to_csv("data.csv", index = None, encoding='utf-8')


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