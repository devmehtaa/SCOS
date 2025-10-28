# Smart-Canteen-Ordering-System

## Problem Addressed
The cafeteria is really rused during Lunch Hour(Peak hours). Orders are processed very slowly. There is a huge waiting line to place your order which causes the food to be prepared a little late. Persoanlly sometimes I have had to go to classes without either finishing my lunch or just not be able to place my order at al.

## Solution Overview
A website based solution is made to address the issue. Where students can place their orders right before leaving for class and their orders can be picked up as soon as they reach the cafeteria. This helps prevent wastage of student time and increase in cafeteria revenue.

## Tech Stack Used
- Backend - Django(Python)
- Frontend - Django templates
- Database - SQL

## Setup 
1. `git clone https://github.com/devmehtaa/SCOS.git` in your terminal to download the codebase locally.
2.  `pip install venv` install venv if not present
3.  `python -m venv venv` to create a virtual env
4.  `venv\Scripts\activate` to activate the venv for windows
5. `pip install -r requirements.txt` to download all dependencies
6. `python manage.py migrate` to initiate the database 
7.  `python manage.py createsuperuser` to create your first user to login
8.  `python manage.py runserver` to start the server
9. `click on the URL provided in the terminal`

## Users
- You can go `/admin` in URL to go to the admin page where you can see the entire database and make new users.
- if you login with a non - staff user you will be redirected to a student page.
- if you login with a staff user then you will be redirected to the staff page.

## Features of SCOS
- Authentication system (Staff & Student Login)
- Staff
    - Select Menu Item 
    - check pending orders
    - account information
- Student
    - Place Orders
    - Payment through Razorpay
    - Account Information

