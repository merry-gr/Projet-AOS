from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import PublicUserSerializer, RegisterSerializer, UserSerializer


# REGISTER
@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.validation_status == 'refused':
        return Response(
            {
                "detail": "Account refused",
                "role": user.role,
                "validation_status": user.validation_status,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "validation_status": user.validation_status,
        }
    )


# GET USERS (PROTECTED)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_users_view(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# Public, minimal user lookup for internal service-to-service calls
@api_view(["GET"])
def api_public_users_view(request):
    qs = User.objects.all().only("id", "username", "role")
    ids = request.GET.get("ids")
    if ids:
        try:
            id_list = [int(x) for x in ids.split(",") if x.strip()]
            qs = qs.filter(id__in=id_list)
        except ValueError:
            return Response({"error": "ids must be comma-separated integers"}, status=400)

    serializer = PublicUserSerializer(qs, many=True)
    return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    return Response({"message": "You are authenticated"})