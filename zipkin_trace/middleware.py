import logging

from django.conf import settings
from py_zipkin.zipkin import zipkin_span
from py_zipkin.thrift import zipkin_core
from requests_futures.sessions import FuturesSession

from . import db_tracing, template_tracing, urllib3_tracing
from . import utils

class ZipkinMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response
		self.logger = logging.getLogger('zipkin')
		self.request_session = FuturesSession()

		db_tracing.init()
		template_tracing.init()
		urllib3_tracing.init()

	def transport_handler(self, span):
		if not getattr(settings, 'ZIPKIN_SERVER', None):
			self.logger.debug('Abandoning, ZIPKIN_SERVER is not set')
			return

		try:
			self.request_session.post(
				self.get_endpoint_url(),
				data=span,
				headers={'Content-Type': 'application/x-thrift'},
				timeout=0.3,
			)
			self.logger.debug('Submitted trace')
		except Exception as e: # pylint: disable=W0702
			self.logger.warning('Cannot submit trace', exc_info=e)

	def __call__(self, request):
		with zipkin_span(**self.get_zipkin_args(request)) as span:
			request.span = span
			response = self.get_response(request)
			span.update_binary_annotations(self.get_response_binary_attrs(response))

		return response

	def get_zipkin_args(self, request):
		return {
			'service_name': self.get_service_name(request),
			'span_name': self.get_span_name(request),
			'binary_annotations': self.get_zipkin_binary_attrs(request),
			'transport_handler': self.transport_handler,
			'port': self.get_port(request),
			'sample_rate': self.get_sample_rate(request),
			'max_span_batch_size': 1 if settings.DEBUG else None,
			'use_128bit_trace_id': True,
			'zipkin_attrs': utils.request_to_zipkinattrs(request),
		}

	def get_response_binary_attrs(self, response):
		out = {
			zipkin_core.HTTP_STATUS_CODE: response.status_code,
		}

		if not response.streaming:
			out[zipkin_core.HTTP_RESPONSE_SIZE] = len(response.content)

		return out

	def get_endpoint_url(self):
		return '{}/api/v1/spans'.format(settings.ZIPKIN_SERVER)

	def get_service_name(self, request):
		return getattr(settings, 'ZIPKIN_SERVICE_NAME', 'Django')

	def get_span_name(self, request):
		return request.path

	def get_zipkin_binary_attrs(self, request):
		return utils.request_to_binary_attrs(request)

	def get_sample_rate(self, request):
		return getattr(settings, 'ZIPKIN_SAMPLE_RATE', 100.0)

	def get_port(self, request):
		return int(request.get_port())

