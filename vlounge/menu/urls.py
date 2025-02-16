from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_home, name='menu_home'),
    path('staff_home/', views.staff_home, name='staff_home'),
    path('student_home/', views.student_home, name='student_home'),
    path('create-food/', views.create_food_item, name='create_food_item'),
    path('remove-from-todays-menu/<int:item_id>/', views.remove_from_todays_menu, name='remove_from_todays_menu'),
    path('add-to-todays-menu/<int:item_id>/', views.add_to_todays_menu, name='add_to_todays_menu')
]
