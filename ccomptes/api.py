# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from flask import Blueprint, render_template, jsonify

from cccomptes.models import Report
from cccomptes.search import search_reports


api = Blueprint('api', __name__)


@api.route('/')
def doc():
    sample = Report.objects.first()
    return render_template('api.html', sample=sample)


@api.route('/search')
def search():
    results = search_reports()
    results['reports'] = [_serialize(a) for a in results['reports']]
    return jsonify(results)


@api.route('/<id>/')
def display(id):
    report = Report.objects.get_or_404(id=id)
    return jsonify(_serialize(report))


def _serialize(report):
    return {
        'id': report.id,
        'juridiction': report.juridiction,
        'types': report.types,
        'publication': report.publication,
        'subject': report.subject,
        'topics': report.topics,
        'tags': report.tags,
        'content': report.content,
    }


def init_app(app):
    app.register_blueprint(api, url_prefix='/api')
