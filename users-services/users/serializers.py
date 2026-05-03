from rest_framework import serializers
from .models import User, VendorProfile, BuyerProfile

# ✅ USER SERIALIZER (affichage complet)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'validation_status', 'date_joined']

# ✅ PUBLIC USER SERIALIZER (pour les recherches simples)
class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role"]

# ✅ REGISTER SERIALIZER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']

    def create(self, validated_data):
        # Normalisation des rôles (gestion des entrées FR et EN)
        raw_role = validated_data.get('role', 'acheteur')
        role_map = {
            'buyer': 'acheteur',
            'vendor': 'vendeur',
            'acheteur': 'acheteur',
            'vendeur': 'vendeur',
            'admin': 'admin'
        }
        role = role_map.get(raw_role.lower(), 'acheteur')

        # Handle email field - if not provided, use username as email for now
        email = validated_data.get('email', validated_data['username'] + '@example.com')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
            password=validated_data['password'],
            role=role
        )
        return user

# ✅ VENDOR PROFILE SERIALIZER
class VendorProfileSerializer(serializers.ModelSerializer):
    # On met 'user' en lecture seule car il est défini par request.user dans la vue
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VendorProfile
        fields = ['user', 'company_name', 'phone', 'address', 'license_number']

# ✅ BUYER PROFILE SERIALIZER
class BuyerProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BuyerProfile
        fields = ['user', 'company_name', 'phone', 'address', 'registration_number', 'buyer_type']