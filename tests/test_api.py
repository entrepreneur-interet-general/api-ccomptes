from flask import url_for

from cccomptes import search


def test_api_doc_empty(client):
    assert client.get(url_for('api.doc')).status_code == 200


def test_api_doc_wih_reports(client, report_factory):
    report_factory.create_batch(3)
    assert client.get(url_for('api.doc')).status_code == 200


def test_search_empty(client):
    assert client.get(url_for('api.search')).status_code == 200


def test_search_with_content(client, report_factory):
    for report in report_factory.create_batch(3):
        search.index(report)
    search.es.indices.refresh(index=search.es.index_name)
    response = client.get(url_for('api.search'))
    assert response.status_code == 200
    assert len(response.json['reports']) == 3


def test_display_report(client, report):
    response = client.get(url_for('api.display', id=report.id))
    assert response.status_code == 200
    assert response.json['id'] == report.id
    assert response.json['subject'] == report.subject
