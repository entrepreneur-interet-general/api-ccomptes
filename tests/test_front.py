from flask import url_for

from cada import search


def test_render_home_empty(client):
    assert client.get(url_for('site.home')).status_code == 200


def test_render_home_with_content(client, report_factory):
    for report in report_factory.create_batch(3):
        search.index(report)
    search.es.indices.refresh(index=search.es.index_name)
    assert client.get(url_for('site.home')).status_code == 200


def test_display_report(client, report):
    assert client.get(url_for('site.display', id=report.id)).status_code == 200


def test_search_empty(client):
    assert client.get(url_for('site.search')).status_code == 200


def test_search_with_content(client, report_factory):
    for report in report_factory.create_batch(3):
        search.index(report)
    search.es.indices.refresh(index=search.es.index_name)
    assert client.get(url_for('site.search')).status_code == 200


def test_sitemap(client, report_factory):
    report_factory.create_batch(3)
    assert client.get(url_for('site.sitemap')).status_code == 200


def test_robots_txt(client):
    assert client.get(url_for('site.robots')).status_code == 200
