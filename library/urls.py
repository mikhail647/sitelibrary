from django.urls import path
from library import views

urlpatterns = [
    # Home/redirect view
    path('', views.home_redirect, name='home'),

    # Authentication views (use Django's built-in views, usually included in project's urls.py)
    # path('login/', views.user_login, name='login'), # Removed - Handled by django.contrib.auth.urls
    # path('logout/', views.user_logout, name='logout'), # Removed - Handled by django.contrib.auth.urls
    path('register/', views.register, name='register'), # Keep our custom registration view

    # Role-based dashboards
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # User Actions
    path('user/myfines/', views.my_fines, name='user_my_fines'),
    # User Book Requests
    path('user/requests/', views.my_requests, name='user_my_requests'),
    path('user/requests/new/', views.request_book, name='user_request_book'),
    # User Interlibrary Loan Requests
    path('user/ill_requests/', views.my_interlibrary_requests, name='user_my_ill_requests'),
    path('user/ill_requests/new/', views.create_interlibrary_request, name='user_create_ill_request'),

    # Staff Actions
    path('staff/issue/', views.issue_book, name='staff_issue_book'),
    path('staff/loans/', views.active_loans, name='staff_active_loans'),
    path('staff/return/<int:loan_id>/', views.return_book, name='staff_return_book'),
    path('staff/return_multiple/', views.return_multiple_books, name='staff_return_multiple'),
    path('staff/fines/', views.manage_fines, name='manage_fines'),
    path('staff/fines/mark_paid/<int:fine_id>/', views.pay_fine, name='mark_fine_paid'),
    path('staff/check_suspensions/', views.staff_check_suspensions, name='staff_check_suspensions'),
    # Book Request Management
    path('staff/requests/', views.manage_requests, name='staff_manage_requests'),
    path('staff/requests/approve/<int:request_id>/', views.approve_request, name='staff_approve_request'),
    path('staff/requests/reject/<int:request_id>/', views.reject_request, name='staff_reject_request'),

    # Interlibrary Loan (ILL) Management for Staff
    path('staff/ill_requests/', views.staff_manage_ill_requests, name='staff_manage_ill_requests'),
    path('staff/ill_requests/update/<int:request_id>/', views.update_ill_request_status, name='staff_update_ill_request_status'),

    # Admin Actions
    path('dashboard/admin/report/', views.generate_report, name='admin_generate_report'),
    path('dashboard/admin/activate_users/', views.activate_users_list, name='admin_activate_users'),
    path('dashboard/admin/activate/<int:user_id>/', views.activate_user, name='admin_activate_user'),

    # Authentication URLs are handled by django.contrib.auth.urls
    # Typically includes: login/, logout/, password_reset/, etc.
    # We might need to override templates later.

    # Add other app-specific URLs below
    # e.g., path('books/', views.book_list, name='book_list'),

] 