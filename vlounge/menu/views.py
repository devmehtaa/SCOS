from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
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
    pending_orders = Order.objects.filter(status="Pending") 
    ready_orders = Order.objects.filter(status="ready") 
    completed_orders = Order.objects.filter(status="Completed") 
    context = {
        'pending_orders': pending_orders,
        'ready_orders': ready_orders,
        'completed_orders': completed_orders
    }

    # if request.method == 'POST':
    #         new_status = request.POST.get("status")
    #         order = Order.objects.get(id)
    #         order.status = new_status
    return render(request, 'staff_orders.html', context)

def update_order_status(request, order_id):
    print("update ran")
    if request.method == 'POST':
        new_status = request.POST.get("status")
        order = get_object_or_404(Order, id=order_id)
        order.status = new_status
        order.save()
        return redirect('staff_orders')
    return render(request, 'staff_orders.html')

def get_filtered_orders(timeframe):
    """Fetches filtered order stats based on timeframe."""
    timeframe_map = {
        "daily": now() - timedelta(days=1),
        "weekly": now() - timedelta(weeks=1),
        "monthly": now() - timedelta(days=30),
        "quarterly": now() - timedelta(days=90),
        "yearly": now() - timedelta(days=365),
        "all": None
    }

    filter_time = timeframe_map.get(timeframe, None)

    if filter_time:
        orders = Order.objects.filter(created_at__gte=filter_time)
    else:
        orders = Order.objects.all()

    pending_orders_count = orders.filter(status="Pending").count()
    ready_orders_count = orders.filter(status="Ready").count()
    completed_orders_count = orders.filter(status="Completed").count()
    total_revenue = orders.filter(status="Completed").aggregate(Sum('total_price'))['total_price__sum'] or 0

    return pending_orders_count, ready_orders_count, completed_orders_count, total_revenue

def get_filtered_users(timeframe):
    """Fetches filtered user stats based on timeframe."""
    timeframe_map = {
        "daily": now() - timedelta(days=1),
        "weekly": now() - timedelta(weeks=1),
        "monthly": now() - timedelta(days=30),
        "quarterly": now() - timedelta(days=90),
        "yearly": now() - timedelta(days=365),
        "all": None
    }

    filter_time = timeframe_map.get(timeframe, None)
    total_users = User.objects.count()
    new_users_count = User.objects.filter(date_joined__gte=filter_time).count() if filter_time else total_users

    return total_users, new_users_count

def dashboard(request):
    
    pending_orders_count, ready_orders_count, completed_orders_count, total_revenue = get_filtered_orders("all")
    total_users, new_users_count = get_filtered_users("all")

    recent_orders = Order.objects.order_by("-created_at")[:5]

    context = {
        "pending_orders_count": pending_orders_count,
        "ready_orders_count": ready_orders_count,
        "completed_orders_count": completed_orders_count,
        "total_revenue": total_revenue,
        "total_users": total_users,
        "new_users_count": new_users_count,
        "recent_orders": recent_orders
    }

    return render(request, "dashboard.html", context)

# def dashboard_stats_api(request):
#     """API endpoint to fetch stats dynamically based on timeframe selection."""
#     timeframe = request.GET.get("timeframe", "all")

#     pending_orders_count, ready_orders_count, completed_orders_count, total_revenue = get_filtered_orders(timeframe)
#     total_users, new_users_count = get_filtered_users(timeframe)

#     return JsonResponse({
#         "pending_orders_count": pending_orders_count,
#         "ready_orders_count": ready_orders_count,
#         "completed_orders_count": completed_orders_count,
#         "total_revenue": total_revenue,
#         "total_users": total_users,
#         "new_users_count": new_users_count
#     })

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
    
    cart_items = Cart.objects.filter(student=request.user)
    if not cart_items.exists():
        return render(request, 'payment_success.html', {"error": "Cart is empty."})
    for cart in cart_items:
        existing_order = Order.objects.filter(student=cart.student, food_item=cart.food_item, status="Pending").first()

        if existing_order:
            existing_order.quantity += cart.quantity
            existing_order.total_price += cart.food_item.price * cart.quantity  # Update total price
            existing_order.save()
        else:
            
            Order.objects.create(
                student=cart.student,
                food_item=cart.food_item,
                quantity=cart.quantity,
                total_price=cart.food_item.price * cart.quantity,  
                status="Pending"
            )
    cart_items.delete()
    return render(request, 'payment_success.html')
    

        

        




