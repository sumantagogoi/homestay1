from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .models import Property, BookingCode, HouseRules, GuestsData, StayData, DocsData
import datetime


def get_default_house_rules(property_obj):
    """
    Return default house rules when property doesn't have custom rules.
    Creates a HouseRules object with default content.
    """
    default_content = """
    <h3>Check-in & Check-out</h3>
    <ul>
    <li>Valid government ID is required at check-in</li>
    <li>Check-in time is after 2:00 PM</li>
    <li>Check-out time is before 11:00 AM</li>
    </ul>

    <h3>House Policies</h3>
    <ul>
    <li>No smoking inside the property</li>
    <li>Quiet hours after 10:00 PM</li>
    <li>Additional guests may incur extra charges</li>
    <li>Damage to property will be charged accordingly</li>
    </ul>
    """.strip()

    # Create default rules for this property
    rules = HouseRules.objects.create(
        property=property_obj,
        title="Terms and Conditions",
        content=default_content,
        version=1
    )
    return rules


@login_required
def dashboard(request):
    """Dashboard view showing recent stays and guest statistics"""
    recent_stays = StayData.objects.all()[:10]
    total_guests = GuestsData.objects.count()
    active_stays = StayData.objects.filter(
        check_out_date__isnull=True
    ).count()

    context = {
        'title': 'Homestay Booking Management',
        'username': request.user.username,
        'recent_stays': recent_stays,
        'total_guests': total_guests,
        'active_stays': active_stays,
    }
    return render(request, 'bookings/dashboard.html', context)


@login_required
def guest_list(request):
    """List all guests"""
    guests = GuestsData.objects.all().order_by('-id')
    context = {
        'title': 'All Guests',
        'guests': guests,
    }
    return render(request, 'bookings/guest_list.html', context)


@login_required
def stay_list(request):
    """List all stays"""
    stays = StayData.objects.all().order_by('-check_in_date')
    context = {
        'title': 'All Stays',
        'stays': stays,
    }
    return render(request, 'bookings/stay_list.html', context)


@login_required
def stay_detail(request, stay_id):
    """View details of a specific stay"""
    stay = get_object_or_404(StayData, id=stay_id)
    context = {
        'title': f'Stay Details - {stay}',
        'stay': stay,
    }
    return render(request, 'bookings/stay_detail.html', context)


@login_required
def new_guest(request):
    """Add a new guest (AJAX endpoint)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            guest = GuestsData.objects.create(name=name)
            return JsonResponse({
                'success': True,
                'guest_id': guest.id,
                'guest_name': guest.name
            })
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def new_stay(request):
    """Create a new stay (AJAX endpoint)"""
    if request.method == 'POST':
        try:
            # Get guest IDs from POST data
            guest_ids = request.POST.getlist('guests[]')

            # Create stay
            stay = StayData.objects.create(
                check_in_date=request.POST.get('check_in_date'),
                check_out_date=request.POST.get('check_out_date') or None,
                phone_number=request.POST.get('phone_number', ''),
                email=request.POST.get('email', ''),
                coming_from=request.POST.get('coming_from', ''),
                terms_agreed=request.POST.get('terms_agreed') == 'true',
                form_filled=request.POST.get('form_filled') == 'true',
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )

            # Add guests to stay
            for guest_id in guest_ids:
                try:
                    guest = GuestsData.objects.get(id=guest_id)
                    stay.guests.add(guest)
                except GuestsData.DoesNotExist:
                    pass

            # Set terms/form datetime if applicable
            if stay.terms_agreed:
                stay.terms_agreed_datetime = datetime.datetime.now()
            if stay.form_filled:
                stay.form_filled_datetime = datetime.datetime.now()
            stay.save()

            return JsonResponse({
                'success': True,
                'stay_id': stay.id,
                'message': 'Stay created successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def upload_document(request):
    """Upload a document (AJAX endpoint)"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            doc = DocsData.objects.create(
                document_name=request.POST.get('document_name', ''),
                document_type=request.POST.get('document_type', 'other'),
                file=request.FILES['file'],
                uploaded_by=request.user,
                notes=request.POST.get('notes', ''),
            )
            return JsonResponse({
                'success': True,
                'doc_id': doc.id,
                'document_name': doc.document_name,
                'filename': doc.filename()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def search_guests(request):
    """Search guests by name (AJAX endpoint)"""
    query = request.GET.get('q', '')
    guests = GuestsData.objects.filter(name__icontains=query)[:10]
    results = [{'id': g.id, 'name': g.name} for g in guests]
    return JsonResponse({'results': results})


@login_required
def delete_customer(request, customer_id):
    """Delete a stay (keeping old endpoint name for compatibility)"""
    if request.method == 'POST':
        try:
            stay = StayData.objects.get(id=customer_id)
            stay.delete()
            return JsonResponse({'success': True, 'message': 'Stay deleted successfully.'})
        except StayData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Stay not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def get_customer_data(request, customer_id):
    """Get stay data (keeping old endpoint name for compatibility)"""
    try:
        stay = StayData.objects.get(id=customer_id)
        data = {
            'guests': [{'id': g.id, 'name': g.name} for g in stay.guests.all()],
            'check_in_date': stay.check_in_date.isoformat(),
            'check_out_date': stay.check_out_date.isoformat() if stay.check_out_date else None,
            'phone_number': stay.phone_number or '',
            'email': stay.email or '',
            'coming_from': stay.coming_from or '',
            'notes': stay.notes or '',
            'terms_agreed': stay.terms_agreed,
            'form_filled': stay.form_filled,
        }
        return JsonResponse({'success': True, 'data': data})
    except StayData.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Stay not found.'})


@login_required
def doc_list(request):
    """List all documents"""
    documents = DocsData.objects.all().order_by('-uploaded_at')
    context = {
        'title': 'All Documents',
        'documents': documents,
    }
    return render(request, 'bookings/doc_list.html', context)


@login_required
def house_rules_management(request):
    """Manage house rules for the property"""
    # For now, we'll get the first property or you could scope by user's group
    # In multi-tenancy, you'd filter by user's property
    try:
        property_obj = Property.objects.first()
        if not property_obj:
            return render(request, 'bookings/house_rules.html', {
                'error': 'No property found. Please create a property first.',
                'house_rules': None
            })

        # Get or create house rules for this property
        try:
            house_rules = property_obj.house_rules
        except HouseRules.DoesNotExist:
            house_rules = get_default_house_rules(property_obj)

        if request.method == 'POST':
            # Update house rules
            house_rules.title = request.POST.get('title', 'Terms and Conditions')
            house_rules.content = request.POST.get('content', '')
            house_rules.version += 1  # Increment version
            house_rules.updated_by = request.user
            house_rules.save()

            return JsonResponse({
                'success': True,
                'message': 'House rules updated successfully!',
                'version': house_rules.version
            })

        context = {
            'title': 'House Rules Management',
            'property': property_obj,
            'house_rules': house_rules,
        }
        return render(request, 'bookings/house_rules.html', context)

    except Exception as e:
        return render(request, 'bookings/house_rules.html', {
            'error': f'Error loading house rules: {str(e)}',
            'house_rules': None
        })


# Main customerInfo view for backward compatibility
@login_required
def customerInfo(request):
    """Main view - showing stays/booking form"""
    if not request.user.is_authenticated:
        return redirect(f'/accounts/login/?next={request.path}')

    stays = StayData.objects.all().order_by('-check_in_date')
    guests = GuestsData.objects.all().order_by('name')

    context = {
        'title': 'Homestay Booking Management',
        'username': request.user.username,
        'stays': stays,
        'guests': guests,
    }
    return render(request, 'bookings/dashboard.html', context)


# Public-facing guest form views (no login required)
def public_guest_form(request, code):
    """
    Public-facing form for guests to fill their information.
    Accessed via booking code like: https://stay.xynocast.com/b/ABc123X/
    """
    try:
        booking_code = BookingCode.objects.select_related('stay', 'stay__property').get(code=code)
        stay = booking_code.stay
        property_obj = stay.property

        # Check if code is valid (not expired)
        if not booking_code.is_valid():
            return render(request, 'bookings/guest_form_expired.html', {
                'error': 'This booking link has expired.',
                'stay': stay
            })

        # Increment access counter
        booking_code.increment_access()

        # Get house rules for this property or use default
        try:
            house_rules = property_obj.house_rules
        except HouseRules.DoesNotExist:
            # Create default rules if none exist
            house_rules = get_default_house_rules(property_obj)

        if request.method == 'POST':
            # Process form submission
            stay.phone_number = request.POST.get('phone_number', '')
            stay.email = request.POST.get('email', '')
            stay.coming_from = request.POST.get('coming_from', '')
            stay.terms_agreed = request.POST.get('terms_agreed') == 'on'
            stay.form_filled = True
            stay.form_filled_datetime = datetime.datetime.now()
            stay.save()

            return render(request, 'bookings/guest_form_success.html', {'stay': stay})

        context = {
            'stay': stay,
            'code': code,
            'house_rules': house_rules,
        }
        return render(request, 'bookings/guest_form.html', context)

    except BookingCode.DoesNotExist:
        return HttpResponseNotFound(render(request, 'bookings/guest_form_expired.html', {
            'error': 'Invalid booking code. Please contact support.'
        }))
