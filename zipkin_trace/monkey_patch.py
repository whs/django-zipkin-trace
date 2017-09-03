from py_zipkin.zipkin import zipkin_span

def wrap(func, binary_annotations=None, **span_args):
	def wrapped(*args, **kwargs):
		current_span_args = span_args

		if callable(binary_annotations):
			current_span_args = current_span_args.copy()
			current_span_args['binary_annotations'] = binary_annotations(*args, **kwargs)

		with zipkin_span(**current_span_args):
			return func(*args, **kwargs)

	return wrapped
