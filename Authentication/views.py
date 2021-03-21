import json
import os
from .cipher import SHA512
from .cipher import AESInstance
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db.models import Q
from django.contrib.auth import login as auth_login
from .models import User
from google.oauth2 import id_token
from google.auth.transport import requests


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')


def user_by_username(request, username):
    if request.method != "GET":
        return JsonResponse({'Allow': ['GET']}, status=405)

    user = User.objects.filter(username=username).first()

    if user is not None:
        return JsonResponse({'exists': True}, status=200)
    return JsonResponse({'exists': False}, status=200)


def user_by_email(request, email):
    if request.method != "GET":
        return JsonResponse({'Allow': ['GET']}, status=405)

    user = User.objects.filter(email=AESInstance.encrypt(email)).first()
    if user is not None:
        return JsonResponse({'exists': True}, status=200)

    return JsonResponse({'exists': False}, status=200)


def user_by_uuid(request, uuid):
    if request.method != "GET":
        return JsonResponse({'Allow': ['GET']}, status=405)

    user = User.objects.filter(uuid=uuid).first()
    if user is not None:
        return JsonResponse({'exists': True, 'user': user.serialize()}, status=200)

    return JsonResponse({'exists': False}, status=200)


def register(request):
    if request.method != "POST":
        return JsonResponse({'Allow': ['POST']}, status=405)

    data = json.loads(request.body.decode('utf-8'))
    user = User.objects.create(username=data['username'], email=AESInstance.encrypt(data['email']),
                               password=SHA512(data['password']))
    auth_login(request, user)
    return JsonResponse({'success': True, 'user': user.uuid}, status=201)


def login(request):
    if request.method != "POST":
        return JsonResponse({'Allow': ['POST']}, status=405)

    data = json.loads(request.body.decode('utf-8'))

    user = User.objects.filter(Q(username=data['username']) | Q(email=AESInstance.encrypt(data['email']))).first()
    if user is not None:
        if user.password is None:
            return JsonResponse({'success': False, 'message': '¡Prueba a iniciar sesión con Google!'}, status=201)
        if user.password == SHA512(data['password']):
            auth_login(request, user)
            return JsonResponse({'success': True, 'user': user.uuid}, status=201)
    return JsonResponse({'success': False, 'message': 'Usuario o contraseña incorrectos'}, status=201)


@ensure_csrf_cookie
def set_csrf_token(request):
    """
    This will be `/api/set-csrf-cookie/` on `urls.py`
    """
    return JsonResponse({"details": "CSRF cookie set"})


def google_login(request):
    if request.method != "POST":
        return JsonResponse({'Allow': ['POST']}, status=405)

    data = json.loads(request.body.decode('utf-8'))
    # Specify the CLIENT_ID of the app that accesses the backend:
    try:
        idinfo = id_token.verify_oauth2_token(data['token'], requests.Request(), GOOGLE_CLIENT_ID)
        print(idinfo)
        user = User.objects.filter(email=AESInstance.encrypt(idinfo['email'])).first()
        if user is None:
            user = User.objects.create(username=idinfo['name'], email=AESInstance.encrypt(idinfo['email']))
            auth_login(request, user)
        return JsonResponse({'success': True, 'user': user.uuid}, status=201)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Token not valid'})
