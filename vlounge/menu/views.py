from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from .models import FoodItem, Order, Cart
from .forms import FoodItemForm
import razorpay


@login_required
def menu_home(request):
    if request.user.is_staff:
        return redirect('staff_home')  # Redirect staff to staff home
    else:
        return redirect('student_home')  # Redirect students to student home
    
# staff section------------------------
@login_required
def staff_home(request):
    print("this ran")
    all_items = FoodItem.objects.filter(is_todays_menu=False)  # Fetch all food items
    todays_menu = FoodItem.objects.filter(is_todays_menu=True)
    context = {
        'all_items': all_items,
        'todays_menu': todays_menu
    }
    return render(request, 'staff_menu.html', context)

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

@login_required
def add_to_todays_menu(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id) 
    food_item.is_todays_menu = True  # Remove from today's menu
    food_item.save()
    return redirect('staff_home') 


def staff_orders(request):
    print("normal ran")
    orders = Order.objects.filter(status="Pending") 
    # if request.method == 'POST':
    #         new_status = request.POST.get("status")
    #         order = Order.objects.get(id)
    #         order.status = new_status
    return render(request, 'staff_orders.html', {'orders': orders})

def update_order_status(request, order_id):
    print("update ran")
    orders = Order.objects.filter(status="Pending") 
    if request.method == 'POST':
        new_status = request.POST.get("status")
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
    return render(request, 'staff_orders.html', {'orders': orders})

# student section--------------------
def student_home(request):
    todays_menu = FoodItem.objects.filter(is_todays_menu=True)  
    return render(request, 'student_menu.html', {'todays_menu':todays_menu})  


def place_order(request):
    cart_items = Cart.objects.filter(student=request.user)  # Fetch all cart items
    total_price = sum(item.food_item.price * item.quantity for item in cart_items)

    context = {'cart_items': cart_items, 'total_price': total_price}
    return render(request, 'cart.html', context)


def thanks(request):
    return render(request, 'thanks.html')

def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart_item, created = Cart.objects.get_or_create(
            student=request.user, food_item=food_item, defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return redirect('place_order')  

    return render(request, 'student_menu.html', {'item': food_item})

def remove_from_cart(request):
    if request.method == 'POST':
        student = request.user
        item_id = request.POST.get('item_id')
        if not item_id:
            return redirect('place_order')
        cart_item = get_object_or_404(Cart, student=student, id=item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('place_order')
    

def create_razorpay_order(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(student=request.user)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.food_item.price * item.quantity for item in cart_items) * 100  # Convert to paise

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {
            "amount": int(total_amount),
            "currency": "INR",
            "payment_capture": "1"  
        }
        order = client.order.create(order_data)

        return JsonResponse({"order_id": order["id"], "amount": total_amount, "currency": "INR"})

    return JsonResponse({"error": "Invalid request"}, status=400)

def payment_success(request):
    Cart.objects.filter(student=request.user).delete()  
    return render(request, 'payment_success.html')
    

        

        




