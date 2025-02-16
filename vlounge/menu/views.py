from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FoodItem
from .forms import FoodItemForm

@login_required
def menu_home(request):
    if request.user.is_staff:
        return redirect('staff_home')  # Redirect staff to staff home
    else:
        return redirect('student_home')  # Redirect students to student home
    
@login_required
def staff_home(request):
    all_items = FoodItem.objects.all()  # Fetch all food items
    todays_menu = FoodItem.objects.filter(is_todays_menu=True)  # Fetch only today's menu items

    context = {
        'all_items': all_items,
        'todays_menu': todays_menu,
    }
    return render(request, 'staff_menu.html', context)

def student_home(request):
    return render(request, 'student_menu.html')  # Student home page

def create_food_item(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_home')  # Redirect to the staff menu page
    else:
        form = FoodItemForm()

    return render(request, 'create_food_item.html', {'form': form})

@login_required
def remove_from_todays_menu(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)  # Get the food item or return 404
    food_item.is_todays_menu = False  # Remove from today's menu
    food_item.save()
    return redirect('staff_home')