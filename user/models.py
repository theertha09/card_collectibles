from django.db import models
import uuid
from form.models import Form  # Consider renaming 'form' to 'Form' for clarity




# Category model (for multi-select)
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# SellerDetailsForm model with ManyToMany category
class SellerDetailsForm(models.Model):
    user = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='seller_details')
    store_name = models.CharField(max_length=255)

    categories = models.ManyToManyField(Category, related_name='sellers') 
    INVENTORY_CHOICES = [
    ('<1000', '<1000 items'),
    ('1000-5000', '1000–5000 items'),
    ('5000+', '5000+ items'),
    ]
    inventory_estimate = models.CharField(max_length=50, choices=INVENTORY_CHOICES)

    specialization = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store_name} - {self.user.full_name}"


