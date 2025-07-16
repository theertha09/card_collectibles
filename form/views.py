from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Form, Address
from .serializers import FormSerializer, AddressSerializer
from rest_framework.permissions import AllowAny


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

# ✅ Registration
class FormRegisterView(generics.CreateAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "code": 201,
            "message": "User registered successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

# ✅ List View with Pagination
class FormListView(generics.ListAPIView):
    queryset = Form.objects.all().order_by('-created_at')
    serializer_class = FormSerializer
    pagination_class = CustomPagination



# ✅ Address List and Create
class AddressListCreateView(generics.ListCreateAPIView):
    queryset = Address.objects.all().select_related('user').order_by('-id')
    serializer_class = AddressSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


# ✅ Address Retrieve, Update, Delete
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all().select_related('user')
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]
