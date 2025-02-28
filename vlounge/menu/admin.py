from django.contrib import admin
from .models import FoodItem, Order, Cart, Stock, FoodIngredient

# Register the model
admin.site.register(FoodItem)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Stock)
admin.site.register(FoodIngredient)