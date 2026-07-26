from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer, Product

# =====================================================================
# (User / Staff / Admin)
# =====================================================================

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_position', 'is_active', 'user_actions')
    @admin.display(description='Position')
    def get_position(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: #d9534f; font-weight: bold; background: #fdf7f7; padding: 4px 10px; border-radius: 4px;">{}</span>', "Admin")
        elif obj.is_staff:
            return format_html('<span style="color: #0275d8; font-weight: bold; background: #f0f7ff; padding: 4px 10px; border-radius: 4px;">{}</span>', "Staff")
        else:
            return format_html('<span style="color: #5cb85c; font-weight: bold; background: #f3faf3; padding: 4px 10px; border-radius: 4px;">{}</span>', "Customer")
    @admin.display(description='Actions')
    def user_actions(self, obj):
        # សំខាន់៖ URL សម្រាប់ Users គឺ admin:auth_user_change
        edit_url = reverse('admin:auth_user_change', args=[obj.pk])
        
        return format_html(
            '<a class="btn btn-sm btn-warning" href="{}" style="color: black; font-weight: bold; background-color: #ffc107; border: none; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Update</a>',
            edit_url
        )
    
    def save_model(self, request, obj, form, change):
        # រក្សាទុក User ចូលក្នុង Database សិន
        super().save_model(request, obj, form, change)
        
        if obj.is_staff or obj.is_superuser:
            Customer.objects.filter(user=obj).delete()
        else:
            # ប្រើ defaults ដើម្បីកំណត់តម្លៃ email ក្នុងពេលបង្កើត
            # វិធីនេះនឹងការពារ Error "NOT NULL constraint failed"
            customer, created = Customer.objects.get_or_create(
                user=obj,
                defaults={
                    'name': obj.username,
                    'email': obj.email if obj.email else f"{obj.username.lower()}@example.com"
                }
            )
            
            # បើមិនមែនជាការបង្កើតថ្មី (Update) ត្រូវ Update តម្លៃដែរ
            if not created:
                customer.name = obj.username
                if obj.email:
                    customer.email = obj.email
                customer.save()
# =====================================================================
# (Customer Admin)
# =====================================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'get_position', 'date_joined')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('date_joined',)
    list_display = ('id', 'name', 'email', 'phone', 'get_position', 'date_joined', 'customer_actions')

    @admin.display(description='Position')
    def get_position(self, obj):
        # ឥឡូវនេះ obj.user មានតម្លៃហើយ (បើអ្នកបានភ្ជាប់ user ទៅ customer)
        if obj.user:
            user = obj.user
            if user.is_superuser:
                return format_html('<span style="color: #d9534f; font-weight: bold; background: #fdf7f7; padding: 4px 10px; border-radius: 4px;">{}</span>', "Admin")
            elif user.is_staff:
                return format_html('<span style="color: #0275d8; font-weight: bold; background: #f0f7ff; padding: 4px 10px; border-radius: 4px;">{}</span>', "Staff")
            else:
                return format_html('<span style="color: #5cb85c; font-weight: bold; background: #f3faf3; padding: 4px 10px; border-radius: 4px;">{}</span>', "Customer")
        return "N/A"
    def customer_actions(self, obj):
        edit_url = reverse('admin:api_customer_change', args=[obj.pk])
        delete_url = reverse('admin:api_customer_delete', args=[obj.pk])
        
        return format_html(
            '<a class="btn btn-sm btn-warning" href="{}" style="color: black; margin-right: 8px; font-weight: bold; background-color: #ffc107; border: none; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Update</a>'
            '<a class="btn btn-sm btn-danger" href="{}" style="color: white; font-weight: bold; background-color: #dc3545; border: none; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Delete</a>',
            edit_url, delete_url
        )

# =====================================================================
# (Product Admin)
# =====================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_image', 'name', 'price', 'product_actions')
    search_fields = ('name',)

    @admin.display(description='Image')
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"

    @admin.display(description='Actions')
    def product_actions(self, obj):
        edit_url = reverse('admin:api_product_change', args=[obj.pk])
        delete_url = reverse('admin:api_product_delete', args=[obj.pk])
        
        return format_html(
            '<a class="btn btn-sm btn-warning" href="{}" style="color: black; margin-right: 8px; font-weight: bold; background-color: #ffc107; border: none; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Update</a>'
            '<a class="btn btn-sm btn-danger" href="{}" style="color: white; font-weight: bold; background-color: #dc3545; border: none; padding: 4px 10px; border-radius: 4px; text-decoration: none;">Delete</a>',
            edit_url, delete_url
        )