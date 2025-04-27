from django.db import models
from django.contrib.auth.models import AbstractUser
from smart_selects.db_fields import ChainedForeignKey
from decimal import Decimal
from django.core.exceptions import ValidationError

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('field_agent', 'Field Agent'),
        ('user', 'User'),  # Chairman
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    nin = models.CharField(max_length=14, unique=True)
    phone_number = models.CharField(max_length=15)
    stage = models.ForeignKey('Stage', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# Location Hierarchy
class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')

    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')

    def __str__(self):
        return self.name

class Subcounty(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='subcounties')

    def __str__(self):
        return self.name

class Stage(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    region = ChainedForeignKey(
        Region,
        chained_field="country",
        chained_model_field="country",
        show_all=False,
        auto_choose=True,
        sort=True,
    )
    district = ChainedForeignKey(
        District,
        chained_field="region",
        chained_model_field="region",
        show_all=False,
        auto_choose=True,
        sort=True,
    )
    subcounty = ChainedForeignKey(
        Subcounty,
        chained_field="district",
        chained_model_field="district",
        show_all=False,
        auto_choose=True,
        sort=True,
    )

    def __str__(self):
        return self.name


# Asset Model
class Asset(models.Model):
    ASSET_TYPE_CHOICES = [
        ("boda", "Boda"),
        ("car", "Car"),
    ]

    STATUS_CHOICES = [
        ('unassigned', 'Unassigned'),
        ('assigned', 'Assigned'),
        ('paid', 'Paid'),
    ]

    asset_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=50, choices=ASSET_TYPE_CHOICES)
    base_value = models.DecimalField(max_digits=10, decimal_places=2)
    selling_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unassigned")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-generate asset_id if not set
        if not self.asset_id:
            last_asset = Asset.objects.filter(asset_id__isnull=False).order_by('id').last()
            if last_asset and last_asset.asset_id:
                last_id = int(last_asset.asset_id[1:])
                self.asset_id = f"A{last_id + 1:05d}"
            else:
                self.asset_id = "A00001"

        # Calculate profit
        if self.base_value is not None and self.selling_value is not None:
            self.profit = self.selling_value - self.base_value

        # Set current balance when creating
        if self._state.adding and self.selling_value:
            self.current_balance = self.selling_value

        # Automatically update status based on assigned_to
        if self.assigned_to:
            self.status = 'assigned'
        else:
            self.status = 'unassigned'

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.type} - {self.asset_id} - {self.name}"




# Payment Model
class Payment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    payment_type = models.CharField(max_length=50)  # e.g., 'installment'
    is_deleted = models.BooleanField(default=False)

    def clean(self):
        if self.asset and self.amount > self.asset.current_balance:
            raise ValidationError(f"Payment exceeds remaining balance of {self.asset.current_balance}.")

    def save(self, *args, **kwargs):
        self.clean()

        asset = self.asset
        asset.current_balance -= self.amount

        if round(asset.current_balance, 2) <= 0:
            asset.current_balance = Decimal("0.00")
            asset.status = 'paid'

        asset.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Payment of {self.amount} for {self.asset.asset_id} on {self.payment_date}"
