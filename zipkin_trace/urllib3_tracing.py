import urllib.parse

from django.conf import settings
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span
from py_zipkin.thrift import zipkin_core

def wrap_urlopen(func):
	parsed_host = None
	if not hasattr(settings, 'ZIPKIN_SERVER'):
		parsed_host = urllib.parse.urlparse(settings.ZIPKIN_SERVER)

	def urlopen(self, method, url, **kw):
		if parsed_host and self.host == parsed_host.hostname:
			# Don't trace zipkin calls
			return func(self, method, url, **kw)

		attrs = {
			zipkin_core.HTTP_HOST: self.host,
			zipkin_core.HTTP_METHOD: method,
			zipkin_core.HTTP_PATH: url,
		}

		with zipkin_span(service_name=self.host, span_name=self._absolute_url(url), binary_annotations=attrs) as span:
			headers = kw['headers'] or {}
			headers.update(create_http_headers_for_new_span())

			if 'headers' in kw:
				del kw['headers']

			try:
				out = func(self, method, url, headers=headers, **kw)

				if hasattr(out.connection, 'sock'):
					peer = out.connection.sock.getpeername()
					span.add_sa_binary_annotation(peer[1], self.host, peer[0])
			except:
				# always add sa_binary even in case of error
				# but if we do it before firing urlopen, then we ended up with two annotations
				span.add_sa_binary_annotation(self.port, self.host)
				raise

			span.update_binary_annotations({
				zipkin_core.HTTP_STATUS_CODE: out.status,
				'http.retries': out.retries,
			})

		return out

	return urlopen

def init():
	HTTPConnectionPool.urlopen = wrap_urlopen(HTTPConnectionPool.urlopen)
	HTTPSConnectionPool.urlopen = wrap_urlopen(HTTPSConnectionPool.urlopen)
