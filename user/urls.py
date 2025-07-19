from django.urls import path
from . import views

urlpatterns = [
    
    # ==================== SELLER DETAILS APIs ====================
    path('sellers/', views.SellerDetailsListCreateView.as_view(), name='seller-list-create'),
    path('sellers/<int:id>/', views.SellerDetailsDetailView.as_view(), name='seller-detail'),
    path('seller/<uuid:user_uuid>/', views.seller_details_by_user, name='seller-by-user'),

    # ==================== CATEGORY APIs ====================
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
]