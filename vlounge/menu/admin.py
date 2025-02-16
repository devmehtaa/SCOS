from django.contrib import admin
from .models import FoodItem, Order # Import your model

# Register the model
admin.site.register(FoodItem)
admin.site.register(Order)
