from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User
from .serializers import UserSerializer

@api_view(["GET", "PUT", "DELETE"])
def get_update_deleteUser(request, uuid):
    try:
        user = User.objects.get(id=uuid)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        data = UserSerializer(user).data
        return Response(data)

    if request.method == "PUT":
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User Updated!!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        user.delete()
        return Response({"message": "User Deleted!!"}, status=status.HTTP_204_NO_CONTENT)

@api_view(["GET", "POST"])
def getAll_createUser(request):
    if request.method == "GET":
        users = User.objects.all()
        data = UserSerializer(users, many=True).data
        if not data:
            return Response({"message": "No Users Found!!"})
        return Response(data)

    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User Created!!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
