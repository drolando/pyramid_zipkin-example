# -*- coding: utf-8 -*-
# frontend.py
import requests

from py_zipkin import Encoding
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.transport import SimpleHTTPTransport
from py_zipkin.zipkin import zipkin_client_span
from wsgiref.simple_server import make_server


@view_config(route_name='call_backend')
def call_backend(request):
    with zipkin_client_span('frontend', 'call_backend'):
        headers = {}
        headers.update(create_http_headers())
        backend_response = requests.get(
            url='http://localhost:9000/api',
            headers=headers,
        )
        return Response(backend_response.text)


def main():
    settings = {}
    settings['service_name'] = 'frontend'
    settings['zipkin.encoding'] = Encoding.V2_JSON
    settings['zipkin.tracing_percent'] = 100.0
    settings['zipkin.transport_handler'] = SimpleHTTPTransport('localhost', 9411)

    config = Configurator(settings=settings)
    config.include('pyramid_zipkin')
    config.add_route('call_backend', '/')
    config.scan()

    app = config.make_wsgi_app()

    server = make_server('0.0.0.0', 8081, app)
    print('Frontend listening on http://localhost:8081')
    server.serve_forever()


if __name__ == '__main__':
    main()
