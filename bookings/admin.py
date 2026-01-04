from django.contrib import admin
from .models import Property, HouseRules, BookingCode, GuestsData, StayData, DocsData


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'phone', 'email', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('created_at',)


@admin.register(HouseRules)
class HouseRulesAdmin(admin.ModelAdmin):
    list_display = ('property', 'title', 'version', 'updated_at', 'updated_by')
    list_filter = ('updated_at', 'property')
    search_fields = ('property__name', 'title')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('property', 'title', 'version')
        }),
        ('Rules Content', {
            'fields': ('content',),
            'description': 'Use the rich text editor to format your house rules. You can add lists, bold text, links, and more.'
        }),
        ('Metadata', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BookingCode)
class BookingCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'stay', 'created_at', 'expires_at', 'accessed_count', 'last_accessed')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('code', 'stay__guests__name')
    readonly_fields = ('code', 'created_at', 'last_accessed', 'get_booking_url')

    def get_booking_url(self, obj):
        """Display the full booking URL"""
        return f"https://stay.xynocast.com{obj.get_absolute_url()}"
    get_booking_url.short_description = 'Booking URL'


@admin.register(GuestsData)
class GuestsDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'property')
    search_fields = ('name',)
    list_filter = ('property',)
    ordering = ('name',)


@admin.register(StayData)
class StayDataAdmin(admin.ModelAdmin):
    list_display = ('get_guest_names', 'property', 'check_in_date', 'check_out_date', 'phone_number', 'terms_agreed', 'form_filled')
    list_filter = ('property', 'check_in_date', 'terms_agreed', 'form_filled', 'created_at')
    search_fields = ('guests__name', 'phone_number', 'email', 'coming_from')
    filter_horizontal = ('guests', 'documents')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'check_in_date'
    fieldsets = (
        ('Property', {
            'fields': ('property',)
        }),
        ('Guest Information', {
            'fields': ('guests', 'guest_count')
        }),
        ('Stay Details', {
            'fields': ('check_in_date', 'check_out_date', 'coming_from')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Documents', {
            'fields': ('documents',)
        }),
        ('Terms & Form Status', {
            'fields': ('terms_agreed', 'terms_agreed_datetime', 'form_filled', 'form_filled_datetime')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def get_guest_names(self, obj):
        return ', '.join([guest.name for guest in obj.guests.all()[:3]])
    get_guest_names.short_description = 'Guests'


@admin.register(DocsData)
class DocsDataAdmin(admin.ModelAdmin):
    list_display = ('document_name', 'property', 'document_type', 'uploaded_at', 'uploaded_by', 'filename')
    list_filter = ('property', 'document_type', 'uploaded_at')
    search_fields = ('document_name', 'notes')
    readonly_fields = ('uploaded_at',)
