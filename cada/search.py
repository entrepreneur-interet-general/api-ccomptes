# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from datetime import datetime

from elasticsearch import Elasticsearch
from flask import current_app, request

from cada.models import Report

log = logging.getLogger(__name__)

MAPPING = {
    'properties': {
        'id': {'type': 'string', 'index': 'not_analyzed'},
        'administration': {
            'type': 'string',
            'analyzer': 'fr_analyzer',
            'fields': {
                'raw': {'type': 'string', 'index': 'not_analyzed'}
            }
        },
        'types': {'type': 'string', 'index': 'not_analyzed'},
        'publication': {
            'type': 'date', 'format': 'YYYY-MM-dd',
            'fields': {
                'raw': {'type': 'string', 'index': 'not_analyzed'}
            }
        },
        'subject': {
            'type': 'string',
            'analyzer': 'fr_analyzer',
            'fields': {
                'raw': {'type': 'string', 'index': 'not_analyzed'}
            }
        },
        'topics': {
            'type': 'string',
            'analyzer': 'fr_analyzer',
            'fields': {
                'raw': {'type': 'string', 'index': 'not_analyzed'}
            }
        },
        'tags': {'type': 'string', 'index': 'not_analyzed'},
        'content': {'type': 'string', 'index': 'not_analyzed'},
        'short_content': {
            'type': 'string',
            'analyzer': 'fr_analyzer',
            'fields': {
                'raw': {'type': 'string', 'index': 'not_analyzed'}
            }
        },
    }
}

FIELDS = (
    'id^5',
    'subject^4',
    'short_content^3',
    'administration',
    'topics',
    'tags',
)

SORTS = {
    'topic': 'topics.raw',
    'administration': 'administration.raw',
    'publication': 'publication',
}

FACETS = {
    'administration': 'administration.raw',
    'type': 'types',
    'tag': 'tags',
    'topic': 'topics.raw',
    'publication': 'publication.raw',
}

ANALSYS = {
    "filter": {
        "fr_stop_filter": {
            "type": "stop",
            "stopwords": ["_french_"]
        },
        "fr_stem_filter": {
            "type": "stemmer",
            "name": "minimal_french"
        }
    },
    "analyzer": {
        "fr_analyzer": {
            "type": "custom",
            "tokenizer": "icu_tokenizer",
            "filter": ["icu_folding", "icu_normalizer", "fr_stop_filter", "fr_stem_filter"],
            "char_filter": ["html_strip"]
        }
    }
}


DOCTYPE = 'report'
DEFAULT_PAGE_SIZE = 20


class ElasticSearch(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('ELASTICSEARCH_URL', 'localhost:9200')
        app.extensions['elasticsearch'] = Elasticsearch([app.config['ELASTICSEARCH_URL']])

    def __getattr__(self, item):
        if 'elasticsearch' not in current_app.extensions.keys():
            raise Exception('not initialised, did you forget to call init_app?')
        return getattr(current_app.extensions['elasticsearch'], item)

    @property
    def index_name(self):
        if current_app.config.get('TESTING'):
            return '{0}-test'.format(current_app.name)
        return current_app.name

    def initialize(self):
        '''Create or update indices and mappings'''
        if es.indices.exists(self.index_name):
            es.indices.put_mapping(index=self.index_name, doc_type=DOCTYPE, body=MAPPING)
        else:
            es.indices.create(self.index_name, {
                'mappings': {'report': MAPPING},
                'settings': {'analysis': ANALSYS},
            })


es = ElasticSearch()


def build_text_queries():
    if not request.args.get('q'):
        return []
    query_string = request.args.get('q')
    if isinstance(query_string, (list, tuple)):
        query_string = ' '.join(query_string)
    return [{
        'multi_match': {
            'query': query_string,
            'fields': FIELDS,
            'analyzer': 'fr_analyzer',
        }
    }]


def build_facet_queries():
    queries = []
    for name, field in FACETS.items():
        if name in request.args:
            value = request.args[name]
            for term in [value] if isinstance(value, basestring) else value:
                queries.append({'term': {field: term}})
    return queries


def build_query():
    must = []
    must.extend(build_text_queries())
    must.extend(build_facet_queries())
    return {'bool': {'must': must}} if must else {'match_all': {}}


def build_aggs():
    return dict([
        (name, {'terms': {'field': field, 'size': 10}})
        for name, field in FACETS.items()
    ])


def build_sort():
    '''Build sort query paramter from kwargs'''
    sorts = request.args.getlist('sort')
    sorts = [sorts] if isinstance(sorts, basestring) else sorts
    sorts = [s.split(' ') for s in sorts]
    return [{SORTS[s]: d} for s, d in sorts if s in SORTS]


def search_reports():
    page = max(int(request.args.get('page', 1)), 1)
    page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    start = (page - 1) * page_size

    result = es.search(index=es.index_name, doc_type=DOCTYPE, body={
        'query': build_query(),
        'aggs': build_aggs(),
        'from': start,
        'size': page_size,
        'sort': build_sort(),
        'fields': [],
    })

    ids = [hit['_id'] for hit in result.get('hits', {}).get('hits', [])]
    reports = Report.objects.in_bulk(ids)
    reports = [reports[id] for id in ids]

    facets = {}
    for name, content in result.get('aggregations', {}).items():
        actives = request.args.get(name)
        actives = [actives] if isinstance(actives, basestring) else actives or []
        facets[name] = [
            (term['key'], term['doc_count'], term['key'] in actives)
            for term in content.get('buckets', [])
        ]

    return {
        'reports': reports,
        'facets': facets,
        'page': page,
        'page_size': page_size,
        'total': result['hits']['total'],
    }


def agg_to_list(result, facet):
    return [
        (t['key'], t['doc_count'])
        for t in
        result.get('aggregations', {}).get(facet, {}).get('buckets', [])
    ]


def ts_to_dt(value):
    '''Convert an elasticsearch timestamp into a Python datetime'''
    if not value:
        return
    return datetime.utcfromtimestamp(value * 1E-3)


def home_data():
    result = es.search(es.index_name, body={
        'query': {'match_all': {}},
        'size': 0,
        'aggs': {
            'type': {
                'terms': {'field': 'type', 'size': 20}
            },
            'tags': {
                'terms': {'field': 'tags', 'size': 20}
            },
            'topics': {
                'terms': {
                    'field': 'topics.raw',
                    "exclude": "/*",  # Exclude subtopics
                    'size': 20,
                }
            },
            "publications": {
                "stats": {
                    "field": "publication"
                }
            }
        },
    })

    publications = result.get('aggregations', {}).get('publications', {})

    return {
        'type': agg_to_list(result, 'type'),
        'topics': agg_to_list(result, 'topics'),
        'tag_cloud': agg_to_list(result, 'tags'),
        'total': result['hits']['total'],
        'publications': {
            'from': ts_to_dt(publications.get('min')),
            'to': ts_to_dt(publications.get('max')),
        },
    }


def index(report):
    '''Index/Reindex a CADA report'''
    topics = []
    for topic in report.topics:
        topics.append(topic)
        parts = topic.split('/')
        if len(parts) > 1:
            topics.append(parts[0])

    try:
        es.index(index=es.index_name, doc_type=DOCTYPE, id=report.id, body={
            'id': report.id,
            'administration': report.administration,
            'types': report.types,
            'publication': report.publication.strftime('%Y-%m-%d'),
            'subject': report.subject,
            'topics': topics,
            'tags': report.tags,
            # The field `content` is sometime too large to be indexed
            #'content': report.content,
            'short_content': report.short_content,
        })
    except:
        log.exception('Unable to index report %s', report.id)
