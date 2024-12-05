# auth required 
# teacher required
# admin required

from rest_framework_simplejwt.tokens import AccessToken
from django.http.response import JsonResponse
from django.contrib.auth.models import User
from api.models import *
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist

from functools import wraps
from django.http import HttpResponseBadRequest, HttpResponseForbidden

def checkAuthorization(auth):
    if auth != 'null':
        get_token = auth.split(" ")[1]
        try:
            token = AccessToken(get_token)
            if token:
                return token
        except Exception:
            return None
    return None

def basic_auth(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if auth:
            token = checkAuthorization(auth)
            if token:
                try:
                    request.current_user = User.objects.get(id=token['user_id'])
                    
                    if request.current_user!=None:
                        return view_func(request, *args, **kwargs)
                    else:
                        return HttpResponseForbidden("Access denied, Token and user do not match")
                except User.DoesNotExist:
                    return JsonResponse({"status_code": 400, "status_msg": "User not found"}, safe=False)
            else:
                return HttpResponseForbidden("Access denied, Authentication header not found or invalid token")
        else:
            return HttpResponseForbidden("Access denied, Authentication header not found")

    return _wrapped_view

def superuser_auth(view_func):
    @basic_auth
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
            if request.current_user.is_superuser:
                request.current_admin = request.current_user
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({"status_code": 400, "status_msg": "User is not authorized to perform this action"}, safe=False)
       

    return _wrapped_view

def teacher_auth(view_func):
    @basic_auth
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        
            if request.current_user.is_staff:
                request.current_teacher = request.current_user
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({"status_code": 400, "status_msg": "User is not authorized to perform this action"}, safe=False)
        
    return _wrapped_view

# @csrf_exempt
# def auth_required(function):
#     @csrf_exempt
#     def wrapper(request,*args,**kwargs):
#         token=None
#         user=None
#         try:
#                 token=request.headers["Authorization"]
            
#         except KeyError:
#             return JsonResponse(status=403,data={"message":"Token missing. Please add Token to header as Authorization : Bearer ..."})
#         try:
#             user=request.GET["user"]
#         except KeyError:
#             return JsonResponse(status=400,data={"message":"User missing. Please add a parameter as user=user_id"})
#         except Exception as e:
#             print(e)
#             return JsonResponse(status=400,data={"message":"User missing. Please add a parameter as user=user_id"})
#         # token=request.headers["Authorization"]
#         # user=request.GET["user"]
#         request.pmp_user=user
#         request.is_admin=False
#         # request.my_user = object
#         authorised=jwt_verify(token,user)
#         if(authorised):
#             return function(request,*args,**kwargs)
#         return JsonResponse({"status_code": 403,"status_msg":"Invalid Token"},status=403, safe=False)
#     return wrapper
