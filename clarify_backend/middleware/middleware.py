class NonHtmlDebugToolbarMiddleware(object):
    """
    Lifted from http://bit.ly/1u9UYmK
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any non-HTML response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    Special handling for json (pretty printing) and
    binary data (only show data length)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import json
        from django.http import HttpResponse
        from io import BytesIO
        from gzip import GzipFile

        response = self.get_response(request)

        if request.GET.get('debug') == '':
            if response['Content-Type'] == 'application/octet-stream':
                new_content = '<html><body>Binary Data, ' \
                    'Length: {}</body></html>'.format(len(response.content))
                response = HttpResponse(new_content)
            elif response['Content-Type'] != 'text/html':
                content = response.content

                # Check for compression
                if 'content-encoding' in response:
                    if response['Content-Encoding'] != 'gzip':
                        return response
                    zbuf = BytesIO(content)
                    del response['Content-Encoding']
                    with GzipFile(mode='rb', compresslevel=6, fileobj=zbuf) \
                            as zfile:
                        content = zfile.read()
                try:
                    json_ = json.loads(content)
                    content = json.dumps(json_, sort_keys=True, indent=2)
                except ValueError:
                    pass
                jquery_script_tag = '<script src="{}"></script>'.format(
                    '/static/build/vendor/lib.min.js'
                )
                response = HttpResponse(
                    '<html><head>{0}<body><span>JSON OUTPUT:</span>'
                    '<pre>{1}</pre></body></html>'.format(
                        jquery_script_tag, content
                    )
                )

        return response