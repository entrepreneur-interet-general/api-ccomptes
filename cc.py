#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:53:09 2017

@author: seiteta
"""

import pandas as pd
import docx
import re
from subprocess import Popen, PIPE


cada = pd.read_csv("cada.csv")


def doc_to_txt(filename):
    '''
        Gets the path of a Word document and returns the text of this document
        
        :param filename: The filename of the doc or docx document
        :type filename: str
        :return: The text of the document
        :rtype: str
        
        :Example:
     
        >>> doc_to_txt("/Users/seiteta/Work/quen-dit-la-cour/reports/jf00097342.doc")
        'This is text from a .doc document'
        >>> doc_to_txt("/Users/seiteta/Work/quen-dit-la-cour/reports/jf00136930.docx")
        'This is text from a .docx document'
        
    '''
    full_text = []
    
    if filename.lower().endswith(".doc"):
        #print("Converting to txt the doc file:" + filename)
        cmd = ['antiword', filename]
        p = Popen(cmd, stdout=PIPE)
        stdout, stderr = p.communicate()
        full_text = stdout.decode()
    elif filename.lower().endswith(".docx"):
        #print("Converting to txt the docx file:" + filename)
        doc = docx.Document(filename)
        for para in doc.paragraphs:
            full_text.append(para.text)
        full_text = '\n'.join(full_text)
    else :
        print("Document extension should be either .doc or .docx")
    return full_text
        
#==============================================================================
# def txt_cleaner(text):
#     '''
#         Gets a text and returns a cleaned text
#         
#         :param text: The dirty text
#         :type text: str
#         :return: The clean text
#         :rtype: str
#         
#         :Example:
#         >>> txt_cleaner('This text have lots of\n\n\n')
#         'This text have lots of   '
#         >>> txt_cleaner('This text have HTML<sup><a href="#fn1"  id="ref1">1</a></sup>')
#         'This text have HTML'
#     '''
#     # Remove new lines
#     new_text = text.replace("\n", " ")
# 
#     # Remove HTML <sup> tags
#     start = "<sup>"
#     end = "</sup>"
#     pattern = '%s(.*?)%s' % (re.escape(start), re.escape(end))
#     new_text = re.sub(pattern, '', new_text)
#     
#     return new_text
# 
# A = txt_cleaner(A)
# B = txt_cleaner(B)
#==============================================================================

def txt_cleaner(text):
     '''
         Gets a text and returns a cleaned text
         
         :param text: The dirty text
         :type text: str
         :return: The clean text
         :rtype: str
         
         :Example:
         >>> txt_cleaner('This text have lots of\n\n\n')
         'This text have lots of   '
         >>> txt_cleaner('<div>This text have HTML</div>')
         'This text have HTML'
     '''
     # Remove new lines
     new_text = text.replace("\n", " ")
 
     # Remove HTML tags
     start = "<"
     end = ">"
     pattern = '%s(.*?)%s' % (re.escape(start), re.escape(end))
     new_text = re.sub(pattern, '', new_text)
     
     return new_text
 

#==============================================================================
# # Build the corpus
# my_path = "/Users/seiteta/Work/quen-dit-la-cour/reports/"
# from os import listdir
# from os.path import isfile, join
# report_filename = [f for f in listdir(my_path) if isfile(join(my_path, f)) and not f.startswith('.')]
# # report_txt = [txt_cleaner(doc_to_txt(my_path + filename)) for filename in report_filename]
# report_txt = [doc_to_txt(my_path + filename) for filename in report_filename]
# corpus = pd.DataFrame(data = report_txt, index = report_filename, columns = ["report"])
#==============================================================================

# Build the corpus
my_path = "/Users/seiteta/Desktop/dossier sans titre/datasession/2 – Données clef USB/donnees_jf/rapports_publics_2016/"

from os import listdir
from os.path import isfile, join
report_filename = [f for f in listdir(my_path) if isfile(join(my_path, f)) and not f.startswith('.')]
# report_txt = [txt_cleaner(doc_to_txt(my_path + filename)) for filename in report_filename]


from bs4 import BeautifulSoup

def html_to_txt(filename):
    print(filename)
    with open(filename, 'r') as html:
        soup = BeautifulSoup(html, 'html.parser')
        full_text = soup.prettify()[586:-18]
    return full_text

report_filename = [filename for filename in report_filename if filename.endswith('.html')]
report_txt = [html_to_txt(my_path + filename) for filename in report_filename]

corpus = pd.DataFrame(data = report_txt, index = report_filename, columns = ["report"])



# Shorten the report for the import in MongoDB
# TODO: fix that
for i in range(len(corpus)):
    report = corpus["report"].iloc[i]
    report = txt_cleaner(report)
    if len(report) > 30000:
        report = report[7:30000]        
    cada["Avis"].iloc[i] = report


cour = cada.head(len(corpus))

for i in range(len(corpus)):
    cour["Numéro de dossier"].iloc[i] = i

cour["Administration"] = "Cour des comptes"
cour["Type"] = "Rapport"
cour["Thème et sous thème"] = "Thème 1"
cour["Mots clés"] = "Mot clé 1"
cour["Objet"] = ""
    
cour.to_csv("cour.csv", index = None)


#
#from sklearn.feature_extraction.text import TfidfVectorizer
#
#
#french = ["alors", "au", "aux", "aucuns", "aussi", "autre", "avant", "avec", "avoir",
#         "bon", "car", "ce", "cela", "ces", "cette", "ceux", "chaque", "ci", "comme",
#         "comment", "dans", "de", "des", "du", "dedans", "dehors", "depuis", "devrait",
#         "doit", "donc", "dos", "début", "elle", "elles", "en", "encore", "essai",
#         "est", "et", "eu", "fait", "faites", "fois", "font", "hors", "ici", "il",
#         "ils", "je", "juste", "la", "le", "les", "leur", "là", "ma", "maintenant",
#         "mais", "mes", "mine", "moins", "mon", "mot", "même", "ni", "nommés",
#         "notre", "nous", "ou", "où", "ont","par", "parce", "pas", "peut", "peu", "plupart",
#         "pour", "pourquoi", "qu","quand", "que", "quel", "quelle", "quelles", "quels",
#         "qui", "sa", "sans", "ses", "seulement", "si", "sien", "son", "sont",
#         "sous", "soyez", "sujet", "sur", "ta", "tandis", "tellement", "tels",
#         "tes", "ton", "tous", "tout", "trop", "très", "tu", "un", "une", "voient", "vont",
#         "votre", "vous", "vu", "ça", "étaient", "état", "étions", "été", "être",
#         "class", "div", "dsn", "jdc", "td", "tr", "sup", "normal", "saisie", "texte"]
#def find_best_phrase(id_report = 0, num_phrases = 10):
#    """
#        Find phrases with the highest tf-idf value
#        Parameters:
#        id_report => ID of a report (integer)
#        num_phrases => Number of phrases to find (integer)
#        ngram => Number of word in the phrases (integer)
#    """
#    
#    # Train the model
#    tf = TfidfVectorizer(analyzer='word', ngram_range=(1,3), min_df = 0, stop_words = french)
#    
#    # Execute the model against our corpus
#    tfidf_matrix =  tf.fit_transform(corpus["report"])
#    feature_names = tf.get_feature_names() 
#    
#    # Build a dense matrix because some operations can't be done on sparse matrix
#    dense = tfidf_matrix.todense()
#    
#    # Select the id_report report
#    report = dense[id_report].tolist()[0]
#
#    # Match feature index with real words
#    phrase_scores = [pair for pair in zip(range(0, len(report)), report) if pair[1] > 0]
#    sorted_phrase_scores = sorted(phrase_scores, key=lambda t: t[1] * -1)
#        
#    # Save num_phrases phrases in a dictionnary
#    best_phrases = {}
#    for phrase, score in [(feature_names[word_id], score) for (word_id, score) in sorted_phrase_scores][:num_phrases]:
#        best_phrases[phrase] = score
#    return best_phrases
#
#
#for i in range(len(corpus)):
#    report = corpus["report"].iloc[i]
#   
#    cour["Avis"].iloc[i] = report
#        
#for i in range(len(corpus)):
#    a = find_best_phrase(i, 5)
#    b = list(a.keys())
#    c = ', '.join(b)
#    
#    cour["Mots clés"].iloc[i] = c






