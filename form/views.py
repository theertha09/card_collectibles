from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db import models
from .models import Form, Address
from .serializers import FormSerializer, AddressSerializer
from rest_framework.views import APIView


# ✅ Enhanced Custom Pagination Class
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'

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
                "nextPage": self.page.next_page_number() if self.page.has_next() else None,
                "previousPage": self.page.previous_page_number() if self.page.has_previous() else None,
                "startIndex": ((self.page.number - 1) * self.get_page_size(self.request)) + 1,
                "endIndex": min(self.page.number * self.get_page_size(self.request), self.page.paginator.count)
            }
        })


# ✅ User Registration with Referral Code Support
class FormRegisterView(generics.CreateAPIView):
    """
    Register new user with optional referral.
    Accepts: referred_by_code (optional) in the payload.
    """
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "code": 201,
            "message": "User registered successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    



    

# ✅ User List View with Pagination
class FormListView(generics.ListAPIView):
    """
    Paginated list of registered users.
    """
    queryset = Form.objects.all().order_by('-created_at')
    serializer_class = FormSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


# ✅ Access user via unique link
@api_view(['GET'])
@permission_classes([AllowAny])
def user_by_unique_link(request, token):
    """
    Access user profile via unique link token.
    Increments click count and returns user data.
    """
    try:
        user = Form.objects.get(unique_link_token=token, is_link_active=True)
        
        # Check if link is expired
        if user.is_link_expired():
            return Response({
                "code": 410,
                "message": "This link has expired"
            }, status=status.HTTP_410_GONE)
        
        # Increment click count
        user.increment_link_clicks()
        
        # Serialize user data
        serializer = FormSerializer(user)
        
        return Response({
            "code": 200,
            "message": "User profile accessed successfully",
            "data": serializer.data,
            "click_count": user.link_click_count
        })
        
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "Invalid or inactive link"
        }, status=status.HTTP_404_NOT_FOUND)


# ✅ Regenerate unique link
@api_view(['POST'])
@permission_classes([AllowAny])
def regenerate_unique_link(request, user_uuid):
    """
    Regenerate unique link for a user.
    """
    try:
        user = Form.objects.get(uuid=user_uuid)
        user.regenerate_unique_link()
        
        serializer = FormSerializer(user)
        return Response({
            "code": 200,
            "message": "Unique link regenerated successfully",
            "data": {
                "unique_link": user.get_unique_link(),
                "unique_link_token": user.unique_link_token,
                "created_at": user.link_created_at
            }
        })
        
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)


# ✅ Referral registration via link with pagination helper
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def referral_registration(request, referral_code):
    """
    Handle referral registration via referral link.
    GET: Show referrer info
    POST: Register new user with referral
    """
    try:
        referrer = Form.objects.get(referral_code=referral_code)
        
        if request.method == 'GET':
            return Response({
                "code": 200,
                "message": "Referrer found",
                "data": {
                    "referrer_name": referrer.full_name,
                    "referral_code": referrer.referral_code,
                    "total_referrals": referrer.referrals.count()
                }
            })
        
        elif request.method == 'POST':
            # Add referral code to registration data
            data = request.data.copy()
            data['referred_by_code'] = referral_code
            
            serializer = FormSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "code": 201,
                    "message": "User registered successfully with referral",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "code": 400,
                    "message": "Registration failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "Invalid referral code"
        }, status=status.HTTP_404_NOT_FOUND)


# ✅ User Referral Dashboard with pagination info
@api_view(['GET'])
@permission_classes([AllowAny])
def user_referral_dashboard(request, user_uuid):
    """
    Dashboard showing all users referred by a specific user.
    Shows User A's referral statistics and recent referrals with pagination link.
    """
    try:
        user = Form.objects.get(uuid=user_uuid)
        
        # Get recent referred users (first 5)
        referred_users = user.referrals.all().order_by('-created_at')[:5]
        
        # Create referral details for recent users
        recent_referral_details = []
        for referred_user in referred_users:
            recent_referral_details.append({
                "uuid": referred_user.uuid,
                "full_name": referred_user.full_name,
                "last_name": referred_user.last_name,
                "email": referred_user.email,
                "phone_number": referred_user.phone_number,
                "gender": referred_user.gender,
                "referred_date": referred_user.created_at,
                "referrer_name": user.full_name
            })
        
        # Calculate stats
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        total_referrals = user.referrals.count()
        recent_referrals = user.referrals.filter(created_at__gte=thirty_days_ago).count()
        
        referral_code = user.referral_code
        qr_code_url = f"http://127.0.0.1:8000/media/qr_codes/{referral_code}_qr.png"
        
        dashboard_data = {
            "uuid": user.uuid,
            "full_name": user.full_name,
            "email": user.email,
            "referral_code": referral_code,
            "unique_link": user.get_unique_link(),
            "referral_link": user.get_referral_link(),
            "qr_code_url": qr_code_url,
            "total_referrals": total_referrals,
            "recent_referrals": recent_referrals,
            "recent_referral_details": recent_referral_details,
            "showing_recent": len(recent_referral_details),
            "pagination_info": {
                "has_more": total_referrals > 5,
                "total_pages": (total_referrals + 9) // 10,
                "paginated_list_endpoint": f"/api/users/{user_uuid}/referrals/"
            }
        }
        
        return Response({
            "code": 200,
            "message": "Referral dashboard data fetched successfully",
            "data": dashboard_data
        })
        
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)


# ✅ Enhanced Paginated Referral List View
class UserReferralListView(generics.ListAPIView):
    """
    Paginated list of users referred by a specific user.
    Supports filtering, sorting, and search.
    """
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_uuid = self.kwargs.get('user_uuid')
        try:
            user = Form.objects.get(uuid=user_uuid)
            queryset = user.referrals.all()
            
            # Add search functionality
            search_query = self.request.query_params.get('search', None)
            if search_query:
                queryset = queryset.filter(
                    models.Q(full_name__icontains=search_query) |
                    models.Q(last_name__icontains=search_query) |
                    models.Q(email__icontains=search_query)
                )
            
            # Add sorting
            sort_by = self.request.query_params.get('sort', '-created_at')
            if sort_by in ['created_at', '-created_at', 'full_name', '-full_name', 'email', '-email']:
                queryset = queryset.order_by(sort_by)
            else:
                queryset = queryset.order_by('-created_at')
            
            return queryset
            
        except Form.DoesNotExist:
            return Form.objects.none()
    
    def get_serializer(self, *args, **kwargs):
        # Custom serializer for referral list
        class ReferralListSerializer:
            def __init__(self, instance, many=False):
                self.instance = instance
                self.many = many
            
            @property
            def data(self):
                if self.many:
                    return [self._serialize_user(user) for user in self.instance]
                else:
                    return self._serialize_user(self.instance)
            
            def _serialize_user(self, user):
                return {
                    "uuid": user.uuid,
                    "full_name": user.full_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "gender": user.gender,
                    "referred_date": user.created_at,
                    "referrer_name": user.referred_by.full_name if user.referred_by else None
                }
        
        return ReferralListSerializer(*args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        user_uuid = self.kwargs.get('user_uuid')
        
        try:
            user = Form.objects.get(uuid=user_uuid)
        except Form.DoesNotExist:
            return Response({
                "code": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add additional metadata to paginated response
            response.data["referrer_info"] = {
                "name": user.full_name,
                "email": user.email,
                "referral_code": user.referral_code,
                "total_referrals": user.referrals.count()
            }
            
            # Add search and sort info if present
            search_query = self.request.query_params.get('search')
            sort_by = self.request.query_params.get('sort', '-created_at')
            
            response.data["filters"] = {
                "search": search_query,
                "sort": sort_by,
                "available_sorts": ["created_at", "-created_at", "full_name", "-full_name", "email", "-email"]
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "Referral list fetched successfully",
            "data": serializer.data,
            "referrer_info": {
                "name": user.full_name,
                "email": user.email,
                "referral_code": user.referral_code,
                "total_referrals": queryset.count()
            }
        })


# ✅ Referral Analytics with paginated recent referrals
@api_view(['GET'])
@permission_classes([AllowAny])
def referral_analytics(request, user_uuid):
    """
    Advanced analytics for referral performance with pagination support.
    """
    try:
        user = Form.objects.get(uuid=user_uuid)
        
        # Get referral data with time-based analysis
        from datetime import datetime, timedelta
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        # Monthly referral counts
        monthly_referrals = user.referrals.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Recent activity
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # Get recent referrals (limited to 10 for analytics)
        recent_referrals_queryset = user.referrals.all().order_by('-created_at')[:10]
        recent_referrals_data = []
        for referred_user in recent_referrals_queryset:
            recent_referrals_data.append({
                "uuid": referred_user.uuid,
                "full_name": referred_user.full_name,
                "email": referred_user.email,
                "referred_date": referred_user.created_at
            })
        
        total_referrals = user.referrals.count()
        
        analytics_data = {
            "referrer_info": {
                "name": user.full_name,
                "email": user.email,
                "referral_code": user.referral_code,
                "referral_link": user.get_referral_link(),
                "link_clicks": user.link_click_count,
                "member_since": user.created_at
            },
            "referral_stats": {
                "total_referrals": total_referrals,
                "today": user.referrals.filter(created_at__date=today).count(),
                "yesterday": user.referrals.filter(created_at__date=yesterday).count(),
                "last_7_days": user.referrals.filter(created_at__date__gte=last_week).count(),
                "last_30_days": user.referrals.filter(created_at__date__gte=last_month).count(),
            },
            "monthly_breakdown": [
                {
                    "month": item['month'].strftime('%Y-%m'),
                    "count": item['count']
                } for item in monthly_referrals
            ],
            "recent_referrals": recent_referrals_data,
            "recent_referrals_info": {
                "showing": len(recent_referrals_data),
                "total_available": total_referrals,
                "full_list_endpoint": f"/api/users/{user_uuid}/referrals/"
            }
        }
        
        return Response({
            "code": 200,
            "message": "Referral analytics fetched successfully",
            "data": analytics_data
        })
        
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)


# ✅ Search Referred Users with Pagination
class SearchReferredUsersView(generics.ListAPIView):
    """
    Paginated search within referred users by name or email.
    """
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_uuid = self.kwargs.get('user_uuid')
        search_query = self.request.query_params.get('q', '')
        
        try:
            user = Form.objects.get(uuid=user_uuid)
            if search_query:
                return user.referrals.filter(
                    models.Q(full_name__icontains=search_query) |
                    models.Q(last_name__icontains=search_query) |
                    models.Q(email__icontains=search_query)
                ).order_by('-created_at')
            else:
                return Form.objects.none()
        except Form.DoesNotExist:
            return Form.objects.none()
    
    def get_serializer(self, *args, **kwargs):
        # Custom serializer for search results
        class SearchResultSerializer:
            def __init__(self, instance, many=False):
                self.instance = instance
                self.many = many
            
            @property
            def data(self):
                if self.many:
                    return [self._serialize_user(user) for user in self.instance]
                else:
                    return self._serialize_user(self.instance)
            
            def _serialize_user(self, user):
                return {
                    "uuid": user.uuid,
                    "full_name": user.full_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "gender": user.gender,
                    "referred_date": user.created_at,
                    "referrer_name": user.referred_by.full_name if user.referred_by else None
                }
        
        return SearchResultSerializer(*args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        user_uuid = self.kwargs.get('user_uuid')
        search_query = self.request.query_params.get('q', '')
        
        # Validate search query
        if not search_query:
            return Response({
                "code": 400,
                "message": "Search query 'q' parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user exists
        try:
            user = Form.objects.get(uuid=user_uuid)
        except Form.DoesNotExist:
            return Response({
                "code": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add search metadata
            response.data["search_info"] = {
                "query": search_query,
                "total_matches": queryset.count(),
                "searching_in": f"{user.full_name}'s referrals"
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": f"Found {queryset.count()} referred users matching '{search_query}'",
            "data": serializer.data,
            "search_info": {
                "query": search_query,
                "total_matches": queryset.count(),
                "searching_in": f"{user.full_name}'s referrals"
            }
        })


# ✅ Function-based search (keeping original function name for URLs)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_referred_users(request, user_uuid):
    """
    Alternative function-based search with manual pagination.
    """
    try:
        user = Form.objects.get(uuid=user_uuid)
        search_query = request.GET.get('q', '')
        
        if not search_query:
            return Response({
                "code": 400,
                "message": "Search query 'q' parameter is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        # Search in referred users
        referred_users = user.referrals.filter(
            models.Q(full_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query)
        ).order_by('-created_at')
        
        # Manual pagination
        total_count = referred_users.count()
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_users = referred_users[start_index:end_index]
        
        # Serialize search results
        search_results = []
        for referred_user in paginated_users:
            search_results.append({
                "uuid": referred_user.uuid,
                "full_name": referred_user.full_name,
                "last_name": referred_user.last_name,
                "email": referred_user.email,
                "phone_number": referred_user.phone_number,
                "gender": referred_user.gender,
                "referred_date": referred_user.created_at,
                "referrer_name": user.full_name
            })
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        has_next = page < total_pages
        has_previous = page > 1
        
        return Response({
            "code": 200,
            "message": f"Found {total_count} referred users matching '{search_query}'",
            "data": search_results,
            "pagination": {
                "total": total_count,
                "page": page,
                "limit": limit,
                "totalPages": total_pages,
                "hasNext": has_next,
                "hasPrevious": has_previous,
                "nextPage": page + 1 if has_next else None,
                "previousPage": page - 1 if has_previous else None,
                "startIndex": start_index + 1 if total_count > 0 else 0,
                "endIndex": min(end_index, total_count)
            },
            "search_info": {
                "query": search_query,
                "total_matches": total_count,
                "searching_in": f"{user.full_name}'s referrals"
            }
        })
        
    except Form.DoesNotExist:
        return Response({
            "code": 404,
            "message": "User not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            "code": 400,
            "message": "Invalid pagination parameters. Page and limit must be integers."
        }, status=status.HTTP_400_BAD_REQUEST)


# ✅ Address List and Create with Pagination
class AddressListCreateView(generics.ListCreateAPIView):
    """
    Create and list addresses with user details and pagination.
    """
    queryset = Address.objects.all().select_related('user').order_by('-id')
    serializer_class = AddressSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add filtering by user
        user_uuid = self.request.query_params.get('user_uuid')
        if user_uuid:
            queryset = queryset.filter(user__uuid=user_uuid)
        
        # Add search functionality
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(address_line1__icontains=search_query) |
                models.Q(address_line2__icontains=search_query) |
                models.Q(city__icontains=search_query) |
                models.Q(state__icontains=search_query) |
                models.Q(user__full_name__icontains=search_query) |
                models.Q(user__email__icontains=search_query)
            )
        
        return queryset


# ✅ Address Detail View (Retrieve, Update, Delete)
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an address.
    """
    queryset = Address.objects.all().select_related('user')
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]


# ✅ User's Addresses List (Paginated)
class UserAddressListView(generics.ListAPIView):
    """
    Get all addresses for a specific user with pagination.
    """
    serializer_class = AddressSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_uuid = self.kwargs.get('user_uuid')
        try:
            user = Form.objects.get(uuid=user_uuid)
            return Address.objects.filter(user=user).order_by('-id')
        except Form.DoesNotExist:
            return Address.objects.none()
    
    def list(self, request, *args, **kwargs):
        user_uuid = self.kwargs.get('user_uuid')
        
        try:
            user = Form.objects.get(uuid=user_uuid)
        except Form.DoesNotExist:
            return Response({
                "code": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add user info to response
            response.data["user_info"] = {
                "uuid": user.uuid,
                "name": user.full_name,
                "email": user.email,
                "total_addresses": queryset.count()
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "message": "User addresses fetched successfully",
            "data": serializer.data,
            "user_info": {
                "uuid": user.uuid,
                "name": user.full_name,
                "email": user.email,
                "total_addresses": queryset.count()
            }
        })
    



# class UserDetailByUUIDView(APIView):
#     """
#     Retrieve, update (full or partial) a user using user_uuid.
#     Supports: GET, PUT, PATCH
#     """
#     permission_classes = [AllowAny]

#     def get_object(self, user_uuid):
#         try:
#             return Form.objects.get(uuid=user_uuid)
#         except Form.DoesNotExist:
#             return None

#     def get(self, request, user_uuid):
#         user = self.get_object(user_uuid)
#         if user:
#             serializer = FormSerializer(user)
#             return Response({
#                 "code": 200,
#                 "message": "User fetched successfully",
#                 "data": serializer.data
#             })
#         return Response({
#             "code": 404,
#             "message": "User not found"
#         }, status=status.HTTP_404_NOT_FOUND)

#     def put(self, request, user_uuid):
#         user = self.get_object(user_uuid)
#         if user:
#             serializer = FormSerializer(user, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "code": 200,
#                     "message": "User updated successfully",
#                     "data": serializer.data
#                 })
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({
#             "code": 404,
#             "message": "User not found"
#         }, status=status.HTTP_404_NOT_FOUND)

#     def patch(self, request, user_uuid):
#         user = self.get_object(user_uuid)
#         if user:
#             serializer = FormSerializer(user, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     "code": 200,
#                     "message": "User partially updated successfully",
#                     "data": serializer.data
#                 })
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({
#             "code": 404,
#             "message": "User not found"
#         }, status=status.HTTP_404_NOT_FOUND)






class UserFullDetailView(APIView):
    """
    Return full user details by UUID:
    - Profile info
    - Referral stats
    - QR code
    - Addresses
    - Recent referred users
    """
    permission_classes = [AllowAny]

    def get(self, request, user_uuid):
        try:
            user = Form.objects.get(uuid=user_uuid)

            # 🟢 Referral stats
            total_referrals = user.referrals.count()
            referral_code = user.referral_code
            referral_link = user.get_referral_link()
            unique_link = user.get_unique_link()
            qr_code_url = f"http://127.0.0.1:8000/media/qr_codes/{referral_code}_qr.png"

            # 🟢 Addresses
            addresses = Address.objects.filter(user=user).order_by('-id')
            address_data = AddressSerializer(addresses, many=True).data

            # 🟢 Recent referrals (last 5)
            recent_referrals = user.referrals.all().order_by('-created_at')[:5]
            recent_referral_data = [{
                "uuid": r.uuid,
                "full_name": r.full_name,
                "email": r.email,
                "created_at": r.created_at,
            } for r in recent_referrals]

            # 🟢 Full response
            return Response({
                "code": 200,
                "message": "User full details fetched successfully",
                "data": {
                    "uuid": str(user.uuid),
                    "full_name": user.full_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "gender": user.gender,
                    "created_at": user.created_at,
                    "referral": {
                        "referral_code": referral_code,
                        "referral_link": referral_link,
                        "unique_link": unique_link,
                        "qr_code_url": qr_code_url,
                        "total_referrals": total_referrals,
                        "recent_referrals": recent_referral_data
                    },
                    "addresses": address_data,
                    "total_addresses": len(address_data)
                }
            })

        except Form.DoesNotExist:
            return Response({
                "code": 404,
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
