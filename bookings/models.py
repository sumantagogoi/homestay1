from django.db import models
from django.contrib.auth.models import User, Group
from django_summernote.fields import SummernoteTextField
import datetime
import random


def generate_booking_code():
    """
    Generate a unique 7-character base58-like code.
    Base58 excludes similar-looking characters: 0, O, I, l
    """
    # Base58 alphabet (Bitcoin style)
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    code = ''.join(random.choices(alphabet, k=7))
    return code


class Property(models.Model):
    """
    Property model for multi-tenancy. Each property represents a homestay/location.
    Users are associated with properties through Django Groups.
    """
    name = models.CharField(max_length=200, unique=True)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='property',
        verbose_name='Associated Group'
    )
    address = models.TextField(blank=True, null=True)
    location_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Google Maps URL',
        help_text='Google Maps location URL for the property'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"


class HouseRules(models.Model):
    """
    House rules for each property. Displayed to guests during form submission.
    One-to-one relationship with Property allows each property to have custom rules.
    """
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name='house_rules',
        verbose_name='Property'
    )
    title = models.CharField(
        max_length=200,
        default='Terms and Conditions',
        verbose_name='Title displayed to guests'
    )
    content = SummernoteTextField(
        help_text='House rules content with rich text editing support.',
        verbose_name='Rules Content'
    )
    version = models.IntegerField(
        default=1,
        help_text='Increment when making major updates'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Last updated by'
    )

    def __str__(self):
        return f"{self.property.name} - House Rules v{self.version}"

    class Meta:
        verbose_name = "House Rules"
        verbose_name_plural = "House Rules"


class BookingCode(models.Model):
    """
    Unique booking codes for sharing with guests.
    Each code links to a StayData booking so guests can self-fill their information.
    """
    code = models.CharField(
        max_length=7,
        unique=True,
        default=generate_booking_code,
        verbose_name='Booking Code'
    )
    stay = models.OneToOneField(
        'StayData',
        on_delete=models.CASCADE,
        related_name='booking_code',
        verbose_name='Associated Stay'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expiration Date',
        help_text='Optional: When should this link expire?'
    )
    accessed_count = models.IntegerField(
        default=0,
        verbose_name='Times Accessed'
    )
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Last Accessed'
    )

    def __str__(self):
        return f"{self.code} - {self.stay}"

    def increment_access(self):
        """Increment the access counter and update last accessed time"""
        self.accessed_count += 1
        self.last_accessed = datetime.datetime.now()
        self.save(update_fields=['accessed_count', 'last_accessed'])

    def is_valid(self):
        """Check if the code is still valid (not expired)"""
        if self.expires_at is None:
            return True
        return datetime.datetime.now() < self.expires_at

    def get_absolute_url(self):
        """Get the public URL for this booking code"""
        return f"/b/{self.code}/"

    class Meta:
        verbose_name = "Booking Code"
        verbose_name_plural = "Booking Codes"
        ordering = ['-created_at']


class GuestsData(models.Model):
    """
    Store guest names only. Names are not unique as guests can stay multiple times.
    Guests are scoped to a property.
    """
    name = models.CharField(max_length=200)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='guests',
        verbose_name='Property'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Guest"
        verbose_name_plural = "Guests"
        ordering = ['name']


class StayData(models.Model):
    """
    Store information about guest stays including dates, contact info,
    terms agreement, and form completion status.
    Stays are scoped to a property.
    """
    GUEST_COUNT_CHOICES = [(i, str(i)) for i in range(1, 21)]  # 1-20 guests

    # Property for multi-tenancy
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='stays',
        verbose_name='Property'
    )

    # Guest information
    guests = models.ManyToManyField(
        GuestsData,
        related_name='stays',
        verbose_name='Guests'
    )
    guest_count = models.IntegerField(
        default=1,
        choices=GUEST_COUNT_CHOICES,
        help_text='Number of guests'
    )

    # Stay dates
    check_in_date = models.DateField(default=datetime.date.today)
    check_out_date = models.DateField(blank=True, null=True)

    # Contact information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Origin/Where coming from
    coming_from = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Where are the guests coming from?'
    )

    # Document references
    documents = models.ManyToManyField(
        'DocsData',
        blank=True,
        related_name='stays',
        verbose_name='Documents'
    )

    # Terms and form flags
    terms_agreed = models.BooleanField(
        default=False,
        verbose_name='Terms read and agreed'
    )
    terms_agreed_datetime = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Terms agreed at'
    )
    form_filled = models.BooleanField(
        default=False,
        verbose_name='Form filled'
    )
    form_filled_datetime = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Form filled at'
    )

    # Additional information
    notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stays'
    )

    def __str__(self):
        guest_names = ', '.join([guest.name for guest in self.guests.all()[:3]])
        if self.guests.count() > 3:
            guest_names += f' (+{self.guests.count() - 3} more)'
        return f"{guest_names} - {self.check_in_date}"

    class Meta:
        verbose_name = "Stay"
        verbose_name_plural = "Stays"
        ordering = ['-check_in_date']


class DocsData(models.Model):
    """
    Store uploaded documents for guests (ID proofs, etc.)
    Files are uploaded to the media directory.
    Documents are scoped to a property.
    """
    DOCUMENT_TYPES = [
        ('aadhaar', 'Aadhaar Card'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('voter_id', 'Voter ID'),
        ('other', 'Other ID'),
    ]

    # Property for multi-tenancy
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Property'
    )

    document_name = models.CharField(
        max_length=200,
        help_text='Descriptive name for the document'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES,
        default='other'
    )
    file = models.FileField(
        upload_to='guest_docs/%Y/%m/%d/',
        verbose_name='Document file'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.document_name} ({self.get_document_type_display()})"

    def filename(self):
        """Return just the filename, not the full path"""
        from os.path import basename
        return basename(self.file.name)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-uploaded_at']
