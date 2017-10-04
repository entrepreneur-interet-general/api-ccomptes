# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import cStringIO as StringIO
import re

from datetime import datetime

from urlparse import urlsplit, urlunsplit

from flask import Blueprint, abort, render_template, url_for, request, flash, Response, redirect
from flask_mail import Attachment, Mail
from flask_wtf import FlaskForm
from jinja2 import Markup
from werkzeug import url_decode, url_encode
from wtforms import TextField, ValidationError

from cccomptes import csv
from cccomptes.models import Report
from cccomptes.search import search_reports, home_data

DEFAULT_PAGE_SIZE = 20

RE_URL = re.compile(r'https?://')


site = Blueprint('site', __name__)
mail = Mail()


@site.app_template_global(name='static')
def static_global(filename):
    return url_for('static', filename=filename)


@site.app_template_global()
@site.app_template_filter()
def url_rewrite(url=None, **kwargs):
    scheme, netloc, path, query, fragments = urlsplit(url or request.url)
    params = url_decode(query)
    for key, value in kwargs.items():
        params.setlist(key, value if isinstance(value, (list, tuple)) else [value])
    return Markup(urlunsplit((scheme, netloc, path, url_encode(params), fragments)))


@site.app_template_global()
@site.app_template_filter()
def url_add(url=None, **kwargs):
    scheme, netloc, path, query, fragments = urlsplit(url or request.url)
    params = url_decode(query)
    for key, value in kwargs.items():
        if value not in params.getlist(key):
            params.add(key, value)
    return Markup(urlunsplit((scheme, netloc, path, url_encode(params), fragments)))


@site.app_template_global()
@site.app_template_filter()
def url_del(url=None, *args, **kwargs):
    scheme, netloc, path, query, fragments = urlsplit(url or request.url)
    params = url_decode(query)
    for key in args:
        params.poplist(key)
    for key, value in kwargs.items():
        lst = params.poplist(key)
        if value in lst:
            lst.remove(value)
        params.setlist(key, lst)
    return Markup(urlunsplit((scheme, netloc, path, url_encode(params), fragments)))


@site.app_template_global()
def in_url(*args, **kwargs):
    scheme, netloc, path, query, fragments = urlsplit(request.url)
    params = url_decode(query)
    return (
        all(arg in params for arg in args)
        and
        all(key in params and params[key] == value for key, value in kwargs.items())
    )


@site.app_template_global()
@site.app_template_filter()
def treeize(topics, sep='/'):
    tree = {}
    for topic in topics:
        parts = topic.split(sep)
        if len(parts) == 1:
            tree[topic] = tree.get(topic, [])
        elif len(parts) == 2:
            if not parts[0] in tree:
                tree[parts[0]] = []
            tree[parts[0]].append(parts[1])
    return [(k, v) for k, v in sorted(tree.items())]


@site.app_template_global()
@site.app_template_filter()
def treeize_facet(topics, sep='/'):
    tree = {}
    for topic, count, active in topics:
        parts = topic.split(sep)
        if len(parts) == 1:
            tree[topic] = {
                'count': count,
                'active': active,
                'subtopics': tree.get(topic, {}).get('subtopics', [])
            }
        elif len(parts) == 2:
            if not parts[0] in tree:
                tree[parts[0]] = {
                    'count': count,
                    'active': active,
                    'subtopics': []
                }
            tree[parts[0]]['subtopics'].append((parts[1], count, active))
    return [
        (t, tree[t]['count'], tree[t]['active'], tree[t]['subtopics'])
        for t in sorted(tree, key=lambda k: tree[k]['count'])
    ]


@site.app_template_global()
def es_date(value):
    return datetime.strptime(value, '%Y-%m-%d').strftime('%d/%m/%Y')


@site.route('/')
def home():
    return render_template('index.html', **home_data())


@site.route('/search')
def search():
    return render_template('search.html', **search_reports())


class AlertAnonForm(FlaskForm):
    details = TextField()

    def validate_details(form, field):
        if RE_URL.search(field.data):
            raise ValidationError("Vous ne pouvez pas soumettre d'URL")


@site.route('/<id>/')
def display(id):
    report = Report.objects.get_or_404(id=id)
    return render_template('report.html', report=report, form=AlertAnonForm())


@site.route('/<id>/alert', methods=['POST'])
def alert(id):
    report = Report.objects.get_or_404(id=id)
    form = AlertAnonForm()
    if form.validate_on_submit():
        csvfile = StringIO.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(csv.ANON_HEADER)
        writer.writerow(csv.to_anon_row(report))
        attachment = Attachment(
            'cccomptes-fix-{0}.csv'.format(report.id),
            'text/csv',
            csvfile.getvalue()
        )
        mail.send_message("Défaut d'anonymisation sur le rapport de la Cour des comptes {0}".format(report.id),
                          recipients=[site.config['ANON_ALERT_MAIL']],
                          html=render_template('anon_alert_mail.html', report=report, details=form.details.data),
                          attachments=[attachment]
                          )
        flash(
            "<strong>Merci pour votre contribution!</strong> Nous avons bien pris en compte votre signalement.",
            'success'
        )
        return redirect(url_for('site.display', id=report.id))
    else:
        abort(400)


@site.route('/robots.txt')
def robots():
    return Response(render_template('robots.txt'), mimetype='text/plain')


@site.route('/sitemap.xml')
def sitemap():
    xml = render_template('sitemap.xml', reports=Report.objects)
    return Response(xml, mimetype='application/xml')


@site.route('/export')
def export_csv():
    def generate():
        csvfile = StringIO.StringIO()
        writer = csv.writer(csvfile)
        # Generate header
        writer.writerow(csv.HEADER)
        yield csvfile.getvalue()

        for report in Report.objects.order_by('id'):
            csvfile = StringIO.StringIO()
            writer = csv.writer(csvfile)
            writer.writerow(csv.to_row(report))
            yield csvfile.getvalue()

    date = datetime.now().date().isoformat()
    headers = {
        b'Content-Disposition': 'attachment; filename=cccomptes-{0}.csv'.format(date),
        # b'X-Accel-Buffering': 'no',
    }
    response = Response(generate(), mimetype="text/csv", headers=headers)
    return response


# @site.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def init_app(app):
    app.errorhandler(400)(page_not_found)
    mail.init_app(app)
    app.register_blueprint(site)
