from django.db import models
import uuid

# UserForm model
class UserForm(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], null=True, blank=True)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


# Category model (for multi-select)
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# SellerDetailsForm model with ManyToMany category
class SellerDetailsForm(models.Model):
    user = models.ForeignKey(UserForm, on_delete=models.CASCADE, related_name='seller_details')
    store_name = models.CharField(max_length=255)

    categories = models.ManyToManyField(Category, related_name='sellers')  # ✅ supports multiple categories

    INVENTORY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Quantity', 'Quantity'),
    ]
    inventory_estimate = models.CharField(max_length=50, choices=INVENTORY_CHOICES)

    specialization = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store_name} - {self.user.full_name}"
