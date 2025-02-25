from django.urls import path
from . import views
from django.shortcuts import render

urlpatterns = [
    path('', views.menu_home, name='menu_home'),
    path('staff_home/', views.staff_home, name='staff_home'),
    path('student_home/', views.student_home, name='student_home'),
    path('create-food/', views.create_food_item, name='create_food_item'),
    path('remove-from-todays-menu/<int:item_id>/', views.remove_from_todays_menu, name='remove_from_todays_menu'),
    path('add-to-todays-menu/<int:item_id>/', views.add_to_todays_menu, name='add_to_todays_menu'),
    path('order/', views.place_order, name='place_order'),
    path('staff/orders/', views.staff_orders, name='staff_orders'),
    path('staff/orders/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('thanks/', views.thanks, name='thanks'),
    path('cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('order/remove_item/', views.remove_from_cart, name='remove_from_cart'),
    path('create-razorpay-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('staff/stock/', views.stock_dasboard, name='stock_dashboard')
]
