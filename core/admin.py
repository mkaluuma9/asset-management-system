from django.contrib import admin
from .models import Country, Region, District, Subcounty, Stage, Asset, Payment, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm



# Register the Country model with customization
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']

# Register the Region model with customization
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['country']
    search_fields = ['name']

# Register the District model with customization
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'region']
    list_filter = ['region']
    search_fields = ['name']

# Register the Subcounty model with customization
@admin.register(Subcounty)
class SubcountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'district']
    list_filter = ['district']
    search_fields = ['name']

# Register the Stage model with customization
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'region', 'district', 'subcounty']
    list_filter = ['country', 'region', 'district', 'subcounty']
    search_fields = ['name']
    ordering = ['country', 'region', 'district', 'subcounty']  # Order by location hierarchy




@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'nin', 'is_active']
    search_fields = ['username', 'email', 'phone_number', 'nin']
    list_filter = ['is_active', 'is_staff', 'is_superuser']  # Filter by status
    ordering = ['username']  # Default ordering by username


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('amount', 'payment_date', 'payment_method', 'payment_type')
    can_delete = False  # Prevent manual deletion from inline
    show_change_link = True  # Allow viewing payment from the inline

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'type', 'base_value', 'selling_value', 'profit', 'status', 'current_balance', 'assigned_to']
    search_fields = ['asset_id', 'name', 'assigned_to__username']
    ordering = ['status', 'selling_value']
    list_filter = ['status', 'assigned_to']
    readonly_fields = ['asset_id', 'profit', 'current_balance']
    inlines = [PaymentInline]

    def get_fields(self, request, obj=None):
        return ['asset_id', 'name', 'type', 'base_value', 'selling_value', 'profit', 'current_balance', 'assigned_to']

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields + ['assigned_to']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)






@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'amount', 'payment_date', 'payment_method', 'payment_type']
    list_filter = ['payment_method', 'payment_type', 'payment_date']
    search_fields = ['asset__asset_id', 'payment_type']
    ordering = ['payment_date']
    readonly_fields = ['payment_date']