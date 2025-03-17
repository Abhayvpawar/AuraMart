from django.contrib import admin

# Register your models here.
from .models import Product,Cart,CartItem,OrderItem,Order,Category,userinfo # Replace with actual model name

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(userinfo)

