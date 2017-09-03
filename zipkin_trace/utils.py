from py_zipkin.zipkin import ZipkinAttrs
from py_zipkin.thrift import zipkin_core

def request_to_zipkinattrs(request):
	try:
		return ZipkinAttrs(
			trace_id=request.META['HTTP_X_B3_TRACEID'],
			span_id=request.META['HTTP_X_B3_SPANID'],
			parent_span_id=request.META['HTTP_X_B3_PARENTSPANID'],
			flags=request.META['HTTP_X_B3_FLAGS'],
			is_sampled=request.META['HTTP_X_B3_SAMPLED'] == '1',
		)
	except KeyError:
		return None

def request_to_binary_attrs(request):
	return {
		zipkin_core.CLIENT_ADDR: request.META['REMOTE_ADDR'],
		zipkin_core.HTTP_HOST: request.get_host(),
		zipkin_core.HTTP_METHOD: request.method,
		zipkin_core.HTTP_PATH: request.path,
		zipkin_core.HTTP_URL: request.build_absolute_uri(),
		zipkin_core.HTTP_REQUEST_SIZE: request.META.get('CONTENT_LENGTH', '0'),
	}
