from django.shortcuts import render
from .models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from uuid import uuid4
from django.http import JsonResponse
import json


@api_view(["GET", "PUT", "DELETE"])
def get_update_deleteUser(request, uuid: uuid4):

    if request.method == "GET":
        data = UserSerializer(User.objects.get(id=uuid)).data
        return Response(data)

    if request.method == "PUT":
        user = User.objects.get(id=uuid)
        
        user.name=request.data['name']
        user.email=request.data['email']
        user.password=request.data['password']
        user.website=request.data['website']
        user.save()

        return JsonResponse({"message": "User Updated!!"})
    
    if request.method == "DELETE":
        User.objects.get(id=uuid).delete()
        return JsonResponse({"message": "User Deleted!!"})

@api_view(["GET", "POST"])
def getAll_createUser(request):

    if request.method == "GET":
        data = UserSerializer(User.objects.all(), many=True)
        return Response(data.data)
    
    if request.method == "POST":
        new_user = User.objects.create(name=request.data['name'], 
                                       email=request.data['email'], 
                                       password=request.data['password'],
                                       website=request.data['website'])
        data = UserSerializer(new_user)
        return JsonResponse({"message": "User Created!!"})


