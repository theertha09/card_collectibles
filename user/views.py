# views.py
from django.shortcuts import render
from django.db import models
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.decorators import api_view
from .models import  SellerDetailsForm, Category
from .serializers import  SellerDetailsFormSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import SellerDetailsForm, Form
from .serializers import SellerDetailsFormSerializer
from rest_framework.response import Response
from rest_framework import status

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



@api_view(['GET'])
@permission_classes([AllowAny])
def seller_details_by_user(request, user_uuid):
    """
    GET /seller/<user_uuid>/ - Fetch all seller entries for a user
    """
    try:
        user = Form.objects.get(uuid=user_uuid)
        sellers = SellerDetailsForm.objects.filter(user=user).order_by('-created_at')
        serializer = SellerDetailsFormSerializer(sellers, many=True)
        return Response({
            "code": 200,
            "message": "Seller details fetched successfully",
            "data": serializer.data
        })
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)
