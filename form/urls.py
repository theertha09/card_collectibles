
from django.urls import path
from .views import FormRegisterView, FormListView,AddressListCreateView,AddressDetailView

urlpatterns = [
    path('register/', FormRegisterView.as_view(), name='form-register'),
    path('list/', FormListView.as_view(), name='form-list'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

]
