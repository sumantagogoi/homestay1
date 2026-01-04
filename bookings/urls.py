from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/x-javascript')),

    # Main views
    path('', views.customerInfo, name='customer_info'),
    path('customers/', views.customerInfo, name='customer_info_alt'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Guest management
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/search/', views.search_guests, name='search_guests'),
    path('guests/new/', views.new_guest, name='new_guest'),

    # Stay management
    path('stays/', views.stay_list, name='stay_list'),
    path('stays/<int:stay_id>/', views.stay_detail, name='stay_detail'),
    path('stays/new/', views.new_stay, name='new_stay'),

    # Document management
    path('documents/', views.doc_list, name='doc_list'),
    path('documents/upload/', views.upload_document, name='upload_document'),

    # House rules management
    path('house-rules/', views.house_rules_management, name='house_rules'),

    # Public guest form (no authentication required)
    path('b/<str:code>/', views.public_guest_form, name='public_guest_form'),

    # Legacy endpoints (for compatibility)
    path('customer/<int:customer_id>/', views.get_customer_data, name='get_customer_data'),
]
