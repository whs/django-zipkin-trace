# Django-zipkin-trace

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPi](https://img.shields.io/pypi/v/django-zipkin-trace.svg)](https://pypi.python.org/pypi/django-zipkin-trace)

Automatically trace your Django application with [py_zipkin](https://github.com/Yelp/py_zipkin)

## Screenshot

Trace running in Zipkin:

![Zipkin](https://i.imgur.com/BbJJq47.png)

Trace running in [Stackdriver Trace](https://cloud.google.com/trace/) using [Zipkin adapter](https://cloud.google.com/trace/docs/zipkin):

![Stackdriver Trace](https://i.imgur.com/sVh6Npl.png)

![Stackdriver Trace Analysis](https://i.imgur.com/1kEL5H9.png)

## Installation

Install this from pip:

```sh
$ pip install django-zipkin-trace
```

(you may want to write this in your requirements.txt)

Then add `zipkin_trace.ZipkinMiddleware` as your topmost middleware and set `ZIPKIN_SERVER` to your Zipkin URL (eg. http://zipkin:9411)

## Supported tracers

These tracers are provided out of the box. No configuration is needed.

- Database query (SQL are logged, but parameters are not)
- urllib3 requests (including the [requests](https://github.com/requests/requests) module)
- Template rendering

## Configuration options

These options can be set in settings.py:

- **ZIPKIN_SERVER**: HTTP URL of Zipkin server
- **ZIPKIN_SERVICE_NAME**: Service name, default to Django
- **ZIPKIN_SAMPLE_RATE**: Sampling rate in percent from 0 - 100, default to 100

## Overriding transport

If you use other Zipkin transport, override `transport_handler(self, span)` in `zipkin_trace.ZipkinMiddleware` to your transport code. See [py_zipkin docs](https://github.com/Yelp/py_zipkin#transport) for example.

By default, py_zipkin will batch 100 traces before sending. This will make traces slow to appear in Zipkin as it needs to collect 100 traces first. If Django debug mode is on, the middleware will disable this buffer.

## Support policy

This library will be deprecated once [opentracing-python](https://github.com/opentracing/opentracing-python) ships a Zipkin-compatible tracer.

## License

Licensed under the [MIT License](LICENSE). Contains code adapted from [django-speedbar](https://github.com/mixcloud/django-speedbar).
