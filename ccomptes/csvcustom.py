# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import unicodecsv

from flask import url_for
from datetime import datetime

from ccomptes.models import Report

from _csv import field_size_limit


HEADER = [
    'Numéro de dossier',
    'Juridiction',
    'Type',
    'Année',
    'Publication',
    'Objet',
    'Thème et sous thème',
    'Mots clés',
    'Rapport',
    'Texte index'
]


ANON_HEADER = ('id', 'url', 'replace', 'with')


def reader(f):
    '''CSV Reader factory for CCOMPTES format'''
    return unicodecsv.reader(f, encoding='utf-8', delimiter=b',', quotechar=b'"')


def writer(f):
    '''CSV writer factory for CCOMPTES format'''
    return unicodecsv.writer(f, encoding='utf-8', delimiter=b',', quotechar=b'"')


def cleanup(text):
    '''Sanitize text field from HTML encoded caracters'''
    return text.replace('&quot;', '"').replace('&amp;', '&').replace('\uf06e', '•')


def from_row(row):
    '''Create an report from a CSV row'''
    subject = (row[5][0].upper() + row[5][1:]) if row[5] else row[5]
    return Report.objects.create(
        id=row[0],
        juridiction=cleanup(row[1]),
        types=cleanup(row[2]).split(', '),
        publication=datetime.strptime(row[4], '%d/%m/%Y'),
        subject=cleanup(subject),
        topics=[t.title() for t in cleanup(row[6]).split(', ')],
        tags=[tag.strip() for tag in row[7].split(',') if tag.strip()],
        content=cleanup(row[8]),
        short_content=cleanup(row[9])
    )


def to_row(report):
    '''Serialize an report into a CSV row'''
    return [
        report.id,
        report.juridiction,
        report.type,
        report.publication.year,
        report.publication.strftime('%d/%m/%Y'),
        report.subject,
        ', '.join(report.topics),
        ', '.join(report.tags),
        report.content,
    ]


def to_anon_row(report):
    return (report.id, url_for('front.display', id=report.id, _external=True), '', '')
