from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    # បន្ថែម field នេះដើម្បីភ្ជាប់ទៅ user
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def remove_customer_if_not_customer(sender, instance, **kwargs):
    # បើ User នេះលែងជា Customer (ក្លាយជា Staff ឬ Admin)
    if instance.is_staff or instance.is_superuser:
        # រកមើលថាគេមានឈ្មោះក្នុងតារាង Customer ទេ
        customer = Customer.objects.filter(user=instance).first()
        if customer:
            customer.delete() # លុបចោលពីតារាង Customer

def manage_customer_record(sender, instance, created, **kwargs):
    # ពិនិត្យមើលថា User នេះជា Staff ឬ Superuser (Admin) ឬអត់
    is_staff_or_admin = instance.is_staff or instance.is_superuser
    
    if is_staff_or_admin:
        # បើជា Staff/Admin ត្រូវលុបចេញពី Customer dashboard បើមាន
        Customer.objects.filter(user=instance).delete()
    else:
        # បើមិនមែន (មានន័យថាជា Customer) ត្រូវបង្កើត Record ក្នុង Customer dashboard
        # យើងប្រើ get_or_create ដើម្បីកុំឱ្យវាបង្កើតស្ទួន
        Customer.objects.get_or_create(
            user=instance,
            defaults={
                'name': instance.username,
                'email': instance.email
            }
        )
# Product list
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True) #for add picture of product
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"