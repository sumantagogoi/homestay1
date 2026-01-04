# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimalist homestay booking management system built with Django 3.2.5. The platform manages guest bookings, document uploads, and property-specific house rules for multi-tenant homestay operations.

**Key Domain Concepts:**
- **Property**: Multi-tenancy unit. Each property is associated with a Django Group. Users belong to property groups to control data access.
- **Stay**: A booking record with check-in/check-out dates, guest list, contact info, and terms agreement status.
- **Guest**: Simple name entity that can be associated with multiple stays over time.
- **Booking Code**: 7-character base58 code (excluding 0, O, I, l) that provides public URL access for guests to self-complete their information.
- **House Rules**: Rich text content (using Summernote) that is property-specific and displayed to guests during form completion.

## Development Commands

**Run development server:**
```bash
python manage.py runserver
```

**Create migrations after model changes:**
```bash
python manage.py makemigrations bookings
python manage.py migrate
```

**Collect static files (after adding new static assets):**
```bash
python manage.py collectstatic
```

**Check for project issues:**
```bash
python manage.py check
```

**Create superuser for Django admin access:**
```bash
python manage.py createsuperuser
```

## Architecture

### Multi-Tenancy Pattern

The system uses Django Groups for property-based data scoping:
- Each `Property` has a OneToOne relationship with a Django `Group`
- All data models (`GuestsData`, `StayData`, `DocsData`) have a ForeignKey to `Property`
- Users should be assigned to property groups to control data visibility
- **Note**: Current implementation doesn't enforce filtering in views - this needs to be added for proper multi-tenancy

### Booking Code System

**Code Generation:**
- Uses Base58 alphabet excluding similar-looking characters: `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`
- 7-character codes provide ~7.8 billion combinations
- Generated via `generate_booking_code()` in `bookings/models.py`

**Public Guest Workflow:**
1. Admin creates a `Stay` booking (via dashboard or Django admin)
2. `BookingCode` is auto-generated with OneToOne to the stay
3. Public URL: `https://stay.xynocast.com/b/{code}/`
4. Guest visits URL, fills form, agrees to house rules
5. On submit: stay record updated with contact info and `form_filled=True`
6. Access tracking: `accessed_count` and `last_accessed` updated on each visit

### Rich Text Editing

**House Rules:**
- Uses `django-summernote` for WYSIWYG editing
- `SummernoteTextField` in `HouseRules` model
- Dashboard interface at `/bookings/house-rules/` for property managers (no Django admin access needed)
- Auto-creates default rules if property has none
- Version tracking on each save

### Frontend Stack

**Dashboard (authenticated users):**
- AdminLTE 3.x with Bootstrap 4
- jQuery 3.6.0
- DataTables for sortable/searchable tables
- AJAX-based CRUD operations (no page redirects)
- Modal-based forms for booking creation/editing

**Public Guest Form:**
- Standalone page with gradient background
- Custom styling (not using AdminLTE)
- Shows property location via Google Maps URL if configured
- Displays property-specific house rules with `|safe` filter for HTML rendering

### Critical File Relationships

**bookings/models.py:**
- `Property` → `HouseRules` (OneToOne)
- `Property` → `GuestsData` (ForeignKey, many guests per property)
- `Property` → `StayData` (ForeignKey, many stays per property)
- `Property` → `DocsData` (ForeignKey, many documents per property)
- `StayData` → `GuestsData` (ManyToMany, multiple guests per stay)
- `StayData` → `DocsData` (ManyToMany, multiple documents per stay)
- `BookingCode` → `StayData` (OneToOne, one code per stay)

**URL Structure:**
- `/` - Main dashboard (requires login)
- `/bookings/guests/` - Guest list
- `/bookings/stays/` - Stay list
- `/bookings/documents/` - Document management
- `/bookings/house-rules/` - House rules editor (rich text)
- `/b/<code>/` - Public guest form (no login required)
- `/admin/` - Django admin interface

### Static File Handling

- **Development**: Django serves static files directly
- **Production**: WhiteNoise middleware serves compressed static files
- **Source files**: `static/` directory (in version control)
- **Collected files**: `staticfiles/` directory (generated, not in version control)
- **Media files**: `media/guest_docs/` for uploaded documents

### Template Hierarchy

```
templates/
├── base.html (minimal base)
├── base-homestay.html (AdminLTE wrapper, extends base.html)
│   └── All dashboard templates extend this
│       ├── bookings/dashboard.html (main booking interface)
│       ├── bookings/guest_list.html
│       ├── bookings/doc_list.html
│       └── bookings/house_rules.html
└── Standalone templates (no base extension)
    ├── bookings/guest_form.html (public form)
    ├── bookings/guest_form_success.html
    └── bookings/guest_form_expired.html
```

## Important Implementation Notes

**House Rules Auto-Creation:**
The `get_default_house_rules()` helper function automatically creates default house rules when a property doesn't have any. This happens both in the dashboard (`house_rules_management`) and public form (`public_guest_form`) views.

**Booking Code Validation:**
Codes have optional `expires_at` field. The `is_valid()` method checks expiration status. Expired codes show a friendly error page.

**Document Uploads:**
Files are stored in `media/guest_docs/` organized by date. The `DocsData` model tracks document type (Aadhaar, Passport, etc.), uploader, and upload timestamp.

**Legacy Endpoints:**
Some views use old names like `customerInfo`, `delete_customer`, `get_customer_data` for backward compatibility with earlier versions of the system.

**Minimalist Design Philosophy:**
The platform prioritizes simplicity and focused functionality. Avoid adding features that don't directly serve core booking management needs. Each feature should have a clear operational purpose.
