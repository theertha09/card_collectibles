from django.db import models
import uuid
from django.contrib.auth.hashers import make_password

class Form(models.Model):  # Use PascalCase for class name
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        null=True,
        blank=True
    )
    password = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def __str__(self):
        return self.full_name




class Address(models.Model):
    user = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True)
    house_name = models.TextField()
    street_name = models.TextField()
    country = models.TextField()
    state=models.TextField()
    pin = models.IntegerField()
    city = models.TextField()
    image = models.ImageField(upload_to='addresses/', null=True, blank=True)

    def __str__(self):
        return str(self.user.full_name) if self.user else "No User"

