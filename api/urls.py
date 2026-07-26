from django.urls import path
from . import views
from .views import login_view
from .views import user_profile
from .views import user_profile, update_profile


urlpatterns = [
    path('products/', views.get_products, name='get_products'),
    #added new
    path('login/', views.CustomLoginView.as_view(), name='api-login'),
    path('login/', login_view, name='login'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/update/', update_profile, name='update_profile'),
]