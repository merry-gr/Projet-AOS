from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, VendorProfile, BuyerProfile
from .serializers import (
    PublicUserSerializer, RegisterSerializer, UserSerializer, 
    VendorProfileSerializer, BuyerProfileSerializer
)

@api_view(['POST'])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "username": user.username,
            "role": user.role,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"detail": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)

    if user.validation_status != 'approved':
        return Response({
            "detail": "Votre compte est en attente ou a été refusé.",
            "validation_status": user.validation_status,
            "reason": user.rejection_reason,
            "role": user.role
        }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "role": user.role
    })

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_api(request):
    user = request.user
    
    # Choix dynamique du profil
    if user.role == 'vendeur':
        profile, _ = VendorProfile.objects.get_or_create(user=user)
        serializer_class = VendorProfileSerializer
    else:
        profile, _ = BuyerProfile.objects.get_or_create(user=user)
        serializer_class = BuyerProfileSerializer

    if request.method == 'GET':
        serializer = serializer_class(profile)
        data = serializer.data
        data['validation_status'] = user.validation_status
        data['rejection_reason'] = user.rejection_reason
        return Response(data)

    if request.method == 'PUT':
        # Update user fields if provided
        user_fields = ['username', 'email', 'role']
        user_updated = False
        
        for field in user_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                user_updated = True
        
        if user_updated:
            user.save()
        
        # Update profile fields
        serializer = serializer_class(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Reset du statut si l'utilisateur corrige ses infos
            user.validation_status = 'pending'
            user.rejection_reason = ""
            user.save()
            
            # Return combined data
            response_data = serializer.data
            response_data['username'] = user.username
            response_data['email'] = user.email
            response_data['role'] = user.role
            response_data['validation_status'] = user.validation_status
            response_data['rejection_reason'] = user.rejection_reason
            
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def public_users_api(request):
    ids = request.GET.get('ids', '').split(',')
    users = User.objects.filter(id__in=ids)
    serializer = PublicUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_users_api(request):
    if not request.user.is_staff:
        return Response({"detail": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        users = User.objects.all().order_by('-date_joined')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not user_id or action not in ['approve', 'reject']:
            return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            if action == 'approve':
                user.validation_status = 'approved'
                user.rejection_reason = ''
                user.save()
                return Response({"message": f"User {user.username} approved"})
            elif action == 'reject':
                if not rejection_reason:
                    return Response({"detail": "Rejection reason is required"}, status=status.HTTP_400_BAD_REQUEST)
                user.validation_status = 'refused'
                user.rejection_reason = rejection_reason
                user.save()
                return Response({"message": f"User {user.username} rejected"})
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)