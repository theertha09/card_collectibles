from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('register/', views.FormRegisterView.as_view(), name='form-register'),
    path('users/', views.FormListView.as_view(), name='form-list'),
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    
    # Unique Links
    path('user/<str:token>/', views.user_by_unique_link, name='user-by-unique-link'),
    path('regenerate-link/<uuid:user_uuid>/', views.regenerate_unique_link, name='regenerate-unique-link'),
    path('refer/<str:referral_code>/', views.referral_registration, name='referral-registration'),

    # Referral Dashboard
    path('dashboard/<uuid:user_uuid>/', views.user_referral_dashboard, name='user-referral-dashboard'),
    path('dashboard/<uuid:user_uuid>/referrals/', views.UserReferralListView.as_view(), name='user-referral-list'),
    path('dashboard/<uuid:user_uuid>/analytics/', views.referral_analytics, name='referral-analytics'),
    path('dashboard/<uuid:user_uuid>/search/', views.search_referred_users, name='search-referred-users'),
]