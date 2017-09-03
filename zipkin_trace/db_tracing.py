from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper
from py_zipkin.zipkin import zipkin_span

class ZipkinCursorWrapper(CursorWrapper):
	def execute(self, sql, params=()):
		with zipkin_span(service_name='SQL', span_name='db-query', binary_annotations=self.get_binary_annotations(sql)):
			return self.cursor.execute(sql, params)

	def executemany(self, sql, param_list):
		with zipkin_span(service_name='SQL', span_name='db-query', binary_annotations=self.get_binary_annotations(sql)):
			return self.cursor.executemany(sql, param_list)

	def get_binary_annotations(self, sql):
		out = {
			'db.instance': self.db.alias,
			'db.statement': sql,
			'db.type': 'sql',
		}

		try:
			out['db.user'] = self.db.settings_dict['USER']
		except KeyError:
			pass

		return out

def wrapped_cursor(original):
	def wrapped(self, *args, **kwargs):
		cursor = original(self, *args, **kwargs)
		return ZipkinCursorWrapper(cursor, self)

	return wrapped

def init():
	BaseDatabaseWrapper.cursor = wrapped_cursor(BaseDatabaseWrapper.cursor)
