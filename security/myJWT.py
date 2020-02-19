import datetime
import jwt
import os
from functools import wraps
from flask import request, Response


# Any endpoint with this decoration requires auth.
def requires_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        auth_token = False
        if not auth_token:
            auth_token = request.headers.get('idToken')
        if not auth_token:
            return Response('Missing Auth Token!\n' 'You have to login with proper credentials', 401,
                            {'WWW-Authenticate': 'Basic realm="Login Required'})

        idToken = auth_token
        request.idToken = idToken
        return f(*args, **kwargs)

    return decorator
