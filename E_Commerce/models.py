from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
# Create your models here.

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cart_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Cart {self.id} - User {self.user.username}"

@receiver(post_save, sender=User)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)  

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(db_default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            product_price = self.product.price
            self.total_price = self.quantity * product_price

        except ObjectDoesNotExist:
            self.total_price = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

class Order(models.Model):
    order_id = models.CharField(max_length=40, unique=True, editable=False, default="")  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:  # Ensure order_id is generated if empty
            self.order_id = secrets.token_hex(10)  # Generates a 20-character unique ID
        super().save(*args, **kwargs)  # Save properly

    def __str__(self):
        return f"Order {self.order_id} - User {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    # def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
    #     return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"
    
class userinfo(models.Model):
    email=models.CharField(max_length=255)
    first_name=models.CharField(max_length=255,db_default=None)
    last_name=models.CharField(max_length=255,db_default=None)
    gender=models.CharField(max_length=10,null=True,db_default=None)
    phone_number=models.CharField(max_length=10,null=True)
    country=models.CharField(max_length=20,null=True,db_default='India')
    address_1=models.TextField(null=True)
    address_2=models.TextField(null=True)

class security_question(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    question=models.CharField(max_length=255, null=False, blank=False)
    answer=models.CharField(max_length=255, null=False, blank=False)