from rest_framework.decorators import api_view, permission_classes, parser_classes # <--- បន្ថែម parser_classes ត្រង់នេះ
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import IntegrityError

from .models import Product
from .serializers import ProductSerializer

# for import function logout when customer login account to frontend
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser # <--- ត្រឹមត្រូវហើយ

class RegisterUserView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        current_user = request.user
        data = request.data
        requested_role = data.get('role', 'customer') 
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if not username or not password:
            return Response({"error": "Please fill in Username and Password."}, status=status.HTTP_400_BAD_REQUEST)
        if requested_role == 'staff':
            if not current_user.is_superuser:
                return Response(
                    {"error": "You do not have permission to create Staff accounts! Only Admins can create them."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        try:
            if User.objects.filter(username=username).exists():
                return Response({"error": "This username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
            
            new_user = User.objects.create_user(username=username, password=password, email=email)
            
            if requested_role == 'staff':
                new_user.is_staff = True
                new_user.save()
                return Response({"message": f"Create an account Staff '{username}' Success!"}, status=status.HTTP_201_CREATED)
            
            else:
                new_user.is_staff = False 
                new_user.save()
                return Response({"message": f"Create an account Customer '{username}' Success!"}, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================================================================
# Web React (Frontend API)
# =====================================================================
@api_view(['GET'])
@permission_classes([AllowAny]) # ឬ IsAuthenticated ទៅតាមតម្រូវការរបស់ប្អូន
def get_products(request):
    """
    សម្រាប់ទាញយកបញ្ជីផលិតផល (Products) ផ្ញើទៅបង្ហាញនៅលើ React
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    សម្រាប់ទាញយកទិន្នន័យ Profile យកទៅបង្ហាញនៅលើ React
    """
    user = request.user
    
    # បង្កើត Profile មួយជាស្វ័យប្រវត្តិ ប្រសិនបើមិនទាន់មានក្នុង Database
    profile, created = Profile.objects.get_or_create(user=user)
    
    # រៀបចំ URL សម្រាប់រូបភាព Profile ឱ្យបានត្រឹមត្រូវ
    image_url = None
    if profile.profile_image:
        image_url = request.build_absolute_uri(profile.profile_image.url)

    profile_data = {
        "username": user.username,
        "last_name": user.last_name or "",
        "email": user.email or "",
        "phone": profile.phone or "", 
        "address": profile.address or "",
        "city": profile.city or "",
        "country": profile.country or "",
        "bio": profile.bio or "",
        "profile_image": image_url, 
    }

    return Response(profile_data, status=status.HTTP_200_OK)

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')      
        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            if user.is_superuser or user.is_staff:
                role = "admin"
            else:
                role = "customer"
                
            return Response({
                "token": token.key,
                "username": user.username,
                "role": role,
                "message": "Login successful!"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Incorrect username or password."
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        role = "admin" if user.is_superuser else "customer"
        
        return Response({
            "token": token.key,
            "username": user.username,
            "role": role
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "error": "Invalid username or password!"
        }, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================
# UI (Login / Register Facebook)
# =====================================================================

def custom_login_page(request):
    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        
        user = authenticate(request, username=username_input, password=password_input)
        
        if user is not None:
            login(request, user)

            if user.is_superuser or user.is_staff:
                return redirect('/admin/')
            else:
                # ១. បង្កើត ឬទាញយក Token របស់ User នេះ
                token, _ = Token.objects.get_or_create(user=user)
                # ២. បញ្ជូន User ទៅកាន់ React ជាមួយនិង Token តែម្តង
                return redirect(f'http://localhost:5173/?token={token.key}&username={user.username}')
        else:
            error_message = "Invalid username or password!"
            
    return render(request, 'api/login.html', {'error': error_message})


def custom_register_page(request):
    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        
        try:
            user = User.objects.create_user(username=username_input, email=email_input, password=password_input)
            user.is_staff = False
            user.is_superuser = False  
            user.save()
            return redirect('/custom-login/')
        except IntegrityError:
            error_message = "Username already exists!"
            
    return render(request, 'api/register.html', {'error': error_message})


# for import function logout when customer login account to frontend
@csrf_exempt 
def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=200)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser]) 
def update_profile(request):
    """
    សម្រាប់ទទួលការកែសម្រួល (Save Changes) រួមទាំងរូបភាពពី React
    """
    user = request.user
    data = request.data
    
    try:
        # ១. Update ទិន្នន័យលើ User Model ដើម
        user.username = data.get('username', user.username)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        
        # ២. Update ទិន្នន័យលើ Profile Model (រូបភាព, លេខទូរសព្ទ, អាសយដ្ឋាន, ...)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.city = data.get('city', profile.city)
        profile.country = data.get('country', profile.country)
        profile.bio = data.get('bio', profile.bio)
        
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
            
        profile.save()
        
        return Response({"message": "Information saved successfully.! 🎉"}, status=status.HTTP_200_OK)
        
    except Exception as e:
        print("Error updating profile:", str(e)) 
        return Response({"error": f"កំហុសប្រព័ន្ធ៖ {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)