from jose import jwt
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import os


SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret secrets from Sherri' #Grabbing my secret key from a private environment

def encode_token(mechanic_id, role='mechanic'):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=5, hours=0), 
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id), 
        'role': role
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f): #f stands for the function that is getting wrapped
    @wraps(f)
    def decoration(*args, **kwargs): #The function that runs before the function that we're wrapping
    
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1] #Accesses the headers, then the "Bearer token" string, we then split into ['Bearer', 'token'] we then index into token

        if not token:
            return jsonify({"error": "token missing from authorization headers"}), 401
        
        try:

            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.mechanic_id = int(data['sub']) #Adding the mechanic_id from the token to the request.
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'token is expired'}), 403
        except jose.exceptions.JWTError:
            return jsonify({'message': 'invalid token'}), 403
        
        return f(*args, **kwargs)
    
    return decoration