from django.template.base import Template
from . import monkey_patch

def get_binary_annotations(self, *args, **kwargs):
	return {
		'template.name': self.name,
	}

def init():
	Template.render = monkey_patch.wrap(Template.render, get_binary_annotations, service_name='Django', span_name='template-render', include=('server',))
