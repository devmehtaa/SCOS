from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_todays_menu = models.BooleanField(default=False)  # Checkbox for today's menu

    def __str__(self):
        return self.name
    
class Order(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Student who placed the order
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)  # Ordered food item
    quantity = models.PositiveIntegerField(default=1)  
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Ready', 'Ready'), ('Completed', 'Completed')], default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.food_item.name} ({self.status})"
    
class Cart(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Student who placed the order
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)  # Ordered food item
    quantity = models.PositiveIntegerField(default=1)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.food_item.name}"
