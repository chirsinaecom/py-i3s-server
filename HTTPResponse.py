from flask import Response, jsonify


class HTTPResponse:
    """
    A class to represent an HTTP response.
    """

    def __init__(self,  body="", status_code=200,
                 content_type='application/json'):
        self.status_code = status_code
        self._response = Response(
            body, status=status_code, content_type=content_type)
        self.body = body
        self.content_type = content_type

    # def __str__(self):
    #     return f"Response(status_code={self.status_code}, body={self.body})"

    def toJSON(self):
        return jsonify(
            self.body)
