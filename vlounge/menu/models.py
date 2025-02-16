from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_todays_menu = models.BooleanField(default=False)  # Checkbox for today's menu

    def __str__(self):
        return self.name
