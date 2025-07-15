from django.urls import path
from . import views

urlpatterns = [
    # ==================== USER FORM APIs ====================
    path('users/', views.UserFormListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:uuid>/', views.UserFormDetailView.as_view(), name='user-detail'),
    
    # ==================== SELLER DETAILS APIs ====================
    path('sellers/', views.SellerDetailsListCreateView.as_view(), name='seller-list-create'),
    path('sellers/<int:id>/', views.SellerDetailsDetailView.as_view(), name='seller-detail'),
    
    # ==================== CATEGORY APIs ====================
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # ==================== CUSTOM ENDPOINTS ====================
    path('users/<uuid:user_uuid>/sellers/', views.user_seller_details, name='user-seller-details'),
    path('categories/<int:category_id>/sellers/', views.sellers_by_category, name='sellers-by-category'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
]