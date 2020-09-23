import jwt
from flask import request, g, jsonify
from config import SECRET
from functools import wraps

def login_required(func):      
    @wraps(func)                   
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization') 
        if access_token is not None:  
            try:
                payload = jwt.decode(access_token, SECRET['SECRET_KEY'], algorithm = SECRET['ALGORITHMS']) 
            except jwt.InvalidTokenError:
                 payload = None     

            if payload is None:
                return Response(status = 401)  

            loginID   = payload['loginID']
            g.loginID = loginID
            
        else:
            return Response(status = 401)  

        return func(*args, **kwargs)
    return decorated_function