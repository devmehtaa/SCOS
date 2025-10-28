from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from .models import FoodItem, Order, Cart, Stock, FoodIngredient
from .forms import FoodItemForm
import razorpay
import requests
from django.http import HttpResponse, HttpResponseBadRequest
import json
from django.views.decorators.csrf import csrf_exempt
from razorpay.errors import SignatureVerificationError


@login_required
def menu_home(request):
    if request.user.is_staff:
        return redirect('staff_home') 
    else:
        return redirect('student_home')  
    
# staff section------------------------
@login_required
def staff_home(request):
    print("this ran")
    all_items = FoodItem.objects.filter(is_todays_menu=False)  
    todays_menu = FoodItem.objects.filter(is_todays_menu=True)
    context = {
        'all_items': all_items,
        'todays_menu': todays_menu
    }
    return render(request, 'staff_menu.html', context)

PEXELS_API_KEY = "your_pexels_api_key"  
PEXELS_URL = "https://api.pexels.com/v1/search"

# I for Calories
USDA_API_KEY = "HFbhAUcbO3U2zMvRqhPHftCYg2QhZbT5jRcvQpwY"
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_FOOD_URL = "https://api.nal.usda.gov/fdc/v1/food"

def fetch_calories(request):
    """Fetch calorie data from USDA API based on food name."""
    if request.method == "GET":
        food_name = request.GET.get("food_name", "").strip()

        print(f"📥 Received food name in Django: {food_name}")  

        if not food_name:
            return JsonResponse({"error": "Food name is required"}, status=400)

        # earch for food ID
        search_params = {
            "query": food_name,
            "api_key": USDA_API_KEY,
            "dataType": ["Survey (FNDDS)", "Foundation", "Branded"]
        }
        search_response = requests.get(USDA_SEARCH_URL, params=search_params)

        if search_response.status_code != 200:
            print("❌ USDA API Error:", search_response.text)
            return JsonResponse({"error": "USDA API error"}, status=500)

        search_data = search_response.json()
        print("🔍 USDA API Search Response:", search_data)  # 

        if "foods" not in search_data or not search_data["foods"]:
            print("❌ No food found for:", food_name)
            return JsonResponse({"calories": 0, "message": "Food not found"})

        # et first food ID
        fdc_id = search_data["foods"][0]["fdcId"]
        print(f" ID: {fdc_id} for {food_name}")

        # etch calorie details using Food ID
        food_response = requests.get(f"{USDA_FOOD_URL}/{fdc_id}?api_key={USDA_API_KEY}")

        if food_response.status_code != 200:
            print("❌ Failed to fetch calorie data:", food_response.text)
            return JsonResponse({"error": "Failed to fetch calorie data"}, status=500)

        food_data = food_response.json()
        print("🔍 USDA API Food Response:", food_data)  
        calories = 0

        
        if "labelNutrients" in food_data and "calories" in food_data["labelNutrients"]:
            calories = food_data["labelNutrients"]["calories"].get("value", 0)

        
        elif "foodNutrients" in food_data:
            for nutrient in food_data["foodNutrients"]:
                if nutrient.get("nutrient", {}).get("name") == "Energy":
                    calories = nutrient.get("amount", 0)
                    break  # Exit loop once found

        print(f"for {food_name}: {calories} kcal")
        print(calories)
        return JsonResponse({"calories": calories})


def create_food_item(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_home')
    return redirect('staff_home')

@login_required
def remove_from_todays_menu(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)  
    food_item.is_todays_menu = False  
    food_item.save()
    return redirect('staff_home')

@login_required
def add_to_todays_menu(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id) 
    food_item.is_todays_menu = True  
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

# dashboard apis -----------

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

# dashboard apis end here-----------


def stock_dasboard(request):
    stock = Stock.objects.all()
    context = {
        "stock_items": stock
    }
    return render(request, 'stock_dashboard.html', context)

# student section--------------------
def student_home(request):
    todays_menu = FoodItem.objects.filter(is_todays_menu=True)  
    print(f"DEBUG: User logged in: {request.user.is_authenticated}") 
    print(f"DEBUG: User object: {request.user}") 
    return render(request, 'student_menu.html', {'todays_menu':todays_menu})  


def place_order(request):
    cart_items_display = []
    total_price = 0

    if request.user.is_authenticated:
        # ✅ SCENARIO A: Fetch from DB for logged-in users
        cart_items_queryset = Cart.objects.filter(student=request.user).select_related('food_item')
        
        for item in cart_items_queryset:
            subtotal = item.food_item.price * item.quantity
            total_price += subtotal
            cart_items_display.append({
                'item': item.food_item,
                'quantity': item.quantity,
                'subtotal': subtotal,
                'db_id': item.id, # Used for removal/checkout for DB items
                'is_session_item': False
            })

    else:
        # 👤 SCENARIO B: Fetch from Session for anonymous users
        session_cart = request.session.get('cart', {})
        for item_id_str, data in session_cart.items():
            try:
                # Look up the food item details needed for display
                food_item = FoodItem.objects.get(id=int(item_id_str))
                subtotal = food_item.price * data['quantity']
                total_price += subtotal
                cart_items_display.append({
                    'item': food_item,
                    'quantity': data['quantity'],
                    'subtotal': subtotal,
                    'item_id': int(item_id_str), # Used for removal/checkout for Session items
                    'is_session_item': True
                })
            except FoodItem.DoesNotExist:
                # Clean up invalid items from the session
                del session_cart[item_id_str]
                request.session.modified = True
                continue

    context = {
        'cart_items': cart_items_display, 
        'total_price': total_price,
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'cart.html', context)


def thanks(request):
    return render(request, 'thanks.html')

def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, id=item_id)

    if request.method == "POST":
        # Ensure 'quantity' is safely retrieved and is an integer
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1 # Default to 1 if input is invalid

        # --- CORE LOGIC CHANGE ---
        if request.user.is_authenticated:
            # ✅ SCENARIO A: LOGGED-IN USER (Use the Database Model)
            cart_item, created = Cart.objects.get_or_create(
                student=request.user, 
                food_item=food_item, 
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

        else:
            # 👤 SCENARIO B: ANONYMOUS USER (Use the Session)
            # Session cart structure: {'5': {'quantity': 2, 'price': 150}, '10': {'quantity': 1, 'price': 200}}
            session_cart = request.session.get('cart', {})
            item_key = str(item_id) # Keys in a session must be strings

            if item_key in session_cart:
                # Item exists, just update quantity
                session_cart[item_key]['quantity'] += quantity
            else:
                # New item, add to cart dict
                session_cart[item_key] = {
                    'quantity': quantity,
                    'price': food_item.price, # Store price to avoid DB lookup later
                    'name': food_item.name
                }
            
            # Save the updated cart back to the session
            request.session['cart'] = session_cart
            request.session.modified = True # Tell Django the session dictionary changed

        return redirect('place_order') 

    # If the request method is GET, just render the menu (optional logic)
    # This return needs to be adjusted based on where the POST form is.
    return redirect('student_home') 

def remove_from_cart(request):
    if request.method == 'POST':
        student = request.user
        item_name = request.POST.get('item_name')
        if not item_name:
            return redirect('place_order')
        
        cart_item = get_object_or_404(Cart, student=student, food_item__name=item_name)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
        return redirect('place_order')
    
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(request):
    print("Razorpay Key ID:", settings.RAZORPAY_KEY_ID)
    print("Razorpay Key Secret:", settings.RAZORPAY_KEY_SECRET)
    if request.method == "POST":
        cart_items = Cart.objects.filter(student=request.user)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty"}, status=400)

        total_amount = sum(item.food_item.price * item.quantity for item in cart_items) * 100  # in paise

        order_data = {
            "amount": int(total_amount),
            "currency": "INR",
            "payment_capture": 1  # auto capture
        }

        razorpay_order = client.order.create(data=order_data)

        return JsonResponse({
            "order_id": razorpay_order.get("id"),
            "amount": total_amount,
            "currency": "INR"
        })

    return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        params_dict = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        }

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)
        except SignatureVerificationError:
            return JsonResponse({'status': 'failure'}, status=400)

        # Payment is verified - process the order here (save order, clear cart, etc.)
        # Example: create Order object for user

        # order = Order.objects.create(user=request.user, ...)
        # cart_items = Cart.objects.filter(student=request.user)
        # Save order details logic here...

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'invalid request'}, status=400)

def stock_management_view(request):
    """Temporary placeholder view for stock management."""
    # Eventually, you will add your actual stock management logic here.
    return HttpResponse("<h1>Stock Management Page - Work In Progress</h1>")
    

        

        




