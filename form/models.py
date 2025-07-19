# models.py
import uuid
import random
import string
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime
from django.conf import settings
import re
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


# Function to generate a unique link token
def generate_unique_link_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def generate_referral_code(full_name):
    """
    Generate referral code: first 4 letters of name + 3-digit number starting from 000
    Example: John Doe -> JOHN000, JOHN001, JOHN002, etc.
    """
    # Clean the name and get first 4 letters
    clean_name = re.sub(r'[^a-zA-Z]', '', full_name.upper())
    name_prefix = clean_name[:4].ljust(4, 'X')  # Pad with X if less than 4 letters
    
    # Find the next available number for this name prefix
    existing_codes = Form.objects.filter(
        referral_code__startswith=name_prefix
    ).values_list('referral_code', flat=True)
    
    # Extract numbers from existing codes
    existing_numbers = []
    for code in existing_codes:
        if len(code) == 7:  # Should be 4 letters + 3 digits
            try:
                number = int(code[4:])
                existing_numbers.append(number)
            except ValueError:
                continue
    
    # Find the next available number
    next_number = 0
    while next_number in existing_numbers:
        next_number += 1
    
    # Format as 3-digit number
    return f"{name_prefix}{next_number:03d}"


class Form(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        null=True,
        blank=True
    )
    
    password = models.CharField(max_length=255)
    
    # ✅ Referral system fields
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='referrals'
    )
    
    # ✅ Unique link fields
    unique_link_token = models.CharField(max_length=32, unique=True, default=generate_unique_link_token)
    link_created_at = models.DateTimeField(default=timezone.now)
    link_expires_at = models.DateTimeField(null=True, blank=True)  # Optional expiration
    link_click_count = models.IntegerField(default=0)  # Track clicks
    is_link_active = models.BooleanField(default=True)  # Enable/disable link
    
    created_at = models.DateTimeField(default=datetime.now)
    
    def save(self, *args, **kwargs):
        # Generate referral code if not exists
        if not self.referral_code:
            self.referral_code = generate_referral_code(self.full_name)
        super().save(*args, **kwargs)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    
    def get_unique_link(self):
        """Generate the full unique link URL"""
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        return f"{base_url}/user/{self.unique_link_token}/"
    
    def get_referral_link(self):
        """Generate referral link using referral code"""
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000/api')
        return f"{base_url}/refer/{self.referral_code}/"
    
    def regenerate_unique_link(self):
        """Regenerate the unique link token"""
        self.unique_link_token = generate_unique_link_token()
        self.link_created_at = timezone.now()
        self.link_click_count = 0
        self.save()
    
    def regenerate_referral_code(self):
        """Regenerate referral code based on current name"""
        self.referral_code = generate_referral_code(self.full_name)
        self.save()
    
    def increment_link_clicks(self):
        """Increment the link click counter"""
        self.link_click_count += 1
        self.save()
    
    def is_link_expired(self):
        """Check if the link has expired"""
        if self.link_expires_at:
            return timezone.now() > self.link_expires_at
        return False
    
    def __str__(self):
        return f"{self.full_name} ({self.email}) - {self.referral_code}"

    def save(self, *args, **kwargs):
        # Generate referral code if not exists
        if not self.referral_code:
            self.referral_code = generate_referral_code(self.full_name)

        super().save(*args, **kwargs)  # Save first so referral_code exists

        # ✅ Generate QR Code if not exists
        if self.referral_code and not self.qr_code_image:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.get_referral_link())
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f"{self.referral_code}_qr.png"

            self.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['qr_code_image'])  # Save QR image only

class Address(models.Model):
    user = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='addresses')
    house_name = models.CharField(max_length=255)
    street_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='address_images/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Address of {self.user.full_name} - {self.city}"