from django.db import models
from django.contrib.auth.models import User
    
class Stock(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ingredient Name
    quantity_available = models.FloatField() 
    reorder_level = models.FloatField(default=1) # Total available quantity
    unit = models.CharField(
        max_length=50,
        choices=[("kg", "Kilograms"), ("g", "Grams"), ("l", "Liters"), ("ml", "Milliliters")]
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity_available} {self.unit})"
    
 
class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_todays_menu = models.BooleanField(default=False) 
    ingredients = models.ManyToManyField(Stock, through='FoodIngredient')


    def __str__(self):
        return self.name
    
class FoodIngredient(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)  # The dish
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)  # The ingredient
    quantity_needed = models.FloatField()  
    unit = models.CharField(
        max_length=50,
        choices=[("kg", "Kilograms"), ("g", "Grams"), ("l", "Liters"), ("ml", "Milliliters")]
    )

    class Meta:
        unique_together = ('food_item', 'stock')  

    def __str__(self):
        return f"{self.food_item.name}: {self.quantity_needed} {self.unit} of {self.stock.name}"
    
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
