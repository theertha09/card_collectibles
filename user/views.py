# views.py
from django.shortcuts import render
from django.db import models
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view
from .models import UserForm, SellerDetailsForm, Category
from .serializers import UserFormSerializer, SellerDetailsFormSerializer, CategorySerializer

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            "code": 200,
            "message": "Data fetched successfully",
            "data": data,
            "pagination": {
                "total": self.page.paginator.count,
                "page": self.page.number,
                "limit": self.get_page_size(self.request),
                "totalPages": self.page.paginator.num_pages,
                "hasNext": self.page.has_next(),
                "hasPrevious": self.page.has_previous(),
            }
        })

# ==================== USER FORM APIs ====================

class UserFormListCreateView(generics.ListCreateAPIView):
    """
    GET: List all users with pagination
    POST: Create a new user
    """
    queryset = UserForm.objects.all().order_by('-created_at')
    serializer_class = UserFormSerializer
    pagination_class = CustomPagination
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "User created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class UserFormDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve user by UUID
    PUT/PATCH: Update user
    DELETE: Delete user
    """
    queryset = UserForm.objects.all()
    serializer_class = UserFormSerializer
    lookup_field = 'uuid'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "Data fetched successfully",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "User updated successfully",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "User deleted successfully"
        }, status=status.HTTP_200_OK)

# ==================== SELLER DETAILS APIs ====================

class SellerDetailsListCreateView(generics.ListCreateAPIView):
    """
    GET: List all seller details with pagination
    POST: Create seller details
    """
    queryset = SellerDetailsForm.objects.all().order_by('-created_at')
    serializer_class = SellerDetailsFormSerializer
    pagination_class = CustomPagination
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "Seller details created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class SellerDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve seller details by ID
    PUT/PATCH: Update seller details
    DELETE: Delete seller details
    """
    queryset = SellerDetailsForm.objects.all()
    serializer_class = SellerDetailsFormSerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "Seller details fetched successfully",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "Seller details updated successfully",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "Seller details deleted successfully"
        }, status=status.HTTP_200_OK)

# ==================== CATEGORY APIs ====================

class CategoryListCreateView(generics.ListCreateAPIView):
    """
    GET: List all categories
    POST: Create a new category
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "Categories fetched successfully",
            "data": serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "Category created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve category by ID
    PUT/PATCH: Update category
    DELETE: Delete category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "message": "Category fetched successfully",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "Category updated successfully",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "Category deleted successfully"
        }, status=status.HTTP_200_OK)

# ==================== CUSTOM VIEWS ====================

@api_view(['GET'])
def user_seller_details(request, user_uuid):
    """
    Get seller details for a specific user by UUID
    """
    try:
        user = UserForm.objects.get(uuid=user_uuid)
        seller_details = SellerDetailsForm.objects.filter(user=user)
        serializer = SellerDetailsFormSerializer(seller_details, many=True)
        return Response({
            "code": 200,
            "message": "User seller details fetched successfully",
            "data": serializer.data
        })
    except UserForm.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def sellers_by_category(request, category_id):
    """
    Get all sellers for a specific category
    """
    try:
        category = Category.objects.get(id=category_id)
        sellers = SellerDetailsForm.objects.filter(categories=category)
        serializer = SellerDetailsFormSerializer(sellers, many=True)
        return Response({
            "code": 200,
            "message": f"Sellers for category '{category.name}' fetched successfully",
            "data": serializer.data
        })
    except Category.DoesNotExist:
        return Response({
            "code": 404,
            "message": "Category not found"
        }, status=status.HTTP_404_NOT_FOUND)



# ==================== STATISTICS VIEWS ====================

@api_view(['GET'])
def dashboard_stats(request):
    """
    Get dashboard statistics
    """
    total_users = UserForm.objects.count()
    total_sellers = SellerDetailsForm.objects.count()
    total_categories = Category.objects.count()
    
    # Categories with seller count
    categories_with_count = []
    for category in Category.objects.all():
        seller_count = category.sellers.count()
        categories_with_count.append({
            'id': category.id,
            'name': category.name,
            'seller_count': seller_count
        })
    
    return Response({
        "code": 200,
        "message": "Dashboard statistics fetched successfully",
        "data": {
            "total_users": total_users,
            "total_sellers": total_sellers,
            "total_categories": total_categories,
            "categories_with_count": categories_with_count
        }
    })