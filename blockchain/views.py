from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Property, Terms, RentalAgreement, UserRequest, Payment
from datetime import date
from decimal import Decimal
from datetime import date, datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta 

def home(request):
    return render(request, 'index.html')

def register_provider(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        address=request.POST.get('address')
        password=request.POST.get('password')
        role='Provider'
        document=request.FILES.get('document')

        if User.objects.filter(email=email).exists():
            return render(request, 'register_provider.html', {'error': 'Sorry....This email is already registered...!!!'})

        User.objects.create(username=name, 
                            email=email, 
                            contact_number=phone, 
                            address=address, 
                            password=password,
                            role=role,
                            verification_status=False, 
                            document=request.FILES.get('document'))
        return redirect('login')
    
    return render(request, 'register_provider.html')

def register_tenant(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        address=request.POST.get('address')
        password=request.POST.get('password')
        role='Tenant'
        document=request.FILES.get('document')

        if User.objects.filter(email=email).exists():
            return render(request, 'register_tenant.html', {'error': 'Sorry....This email is already registered...!!!'})

        User.objects.create(username=name, 
                            email=email, 
                            contact_number=phone, 
                            address=address, 
                            password=password,
                            role=role,
                            verification_status=False,
                            document=document)
        return redirect('login')
    return render(request, 'register_tenant.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
             return render(request, 'login.html', {'error': "User with this email does not exist."})
        
        if password == user.password:
            login(request, user)
            
            if user.role == 'Provider':
                if user.verification_status == True:
                    return redirect('provider_index')
                else:
                    return render(request, 'login.html', {'error': "Your approval status is still pending"})

            if user.role == 'Tenant':
                if user.verification_status == True:
                    return redirect('tenant_index')
                else:
                    return render(request, 'login.html', {'error': "Your approval status is still pending"})
                
        elif user.check_password(password):
            login(request, user)

            # Check if the user is a superuser
            if user.is_superuser:
                return redirect('admin')
        else:
            return render(request, 'login.html', {'error': "Incorrect email or password"})
        
    return render(request, 'login.html')

def user_logout(request):
    logout(request)  
    return redirect('home')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def provider_index(request):
    return render(request, 'provider_index.html')

@login_required
def tenant_index(request):
    return render(request, 'tenant_index.html')

@login_required
def admin_approval(request):
    providers = User.objects.filter(role='Provider', verification_status=False)
    tenants = User.objects.filter(role='Tenant', verification_status=False)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        user = User.objects.get(id=user_id)

        if action == "approve":
            user.verification_status = True
            user.save()
        return redirect("admin_approval")  
    
    return render(request, 'admin_approval.html', {'providers': providers, 'tenants': tenants})

@login_required
def add_property(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        address = request.POST.get('address')
        rent_amount = request.POST.get('rent_amount')
        image = request.FILES.get('image')

        property = Property.objects.create(provider=request.user,
                                           title=title, 
                                           description=description,
                                           address=address,
                                           rent_amount=rent_amount,
                                           image=image)
        property.save()
        return render(request, 'add_property.html', {'success': 'Your Property added successfully.....'})
    return render(request, 'add_property.html')

@login_required
def property_approvel(request):
    properties = Property.objects.filter(is_approved=False)
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        action=request.POST.get('action')
        property = get_object_or_404(Property, id=property_id)

        if action == 'approve':
            property.is_approved = True
            property.save()
            return render(request, 'property_approvel.html', {'properties': properties})
        elif action == 'reject':
            property.delete()
            return render(request, 'property_approvel.html', {'properties': properties})

    return render(request, 'property_approvel.html', {'properties': properties})

@login_required
def manage_properties(request):
    properties = Property.objects.filter(provider=request.user)

    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        action=request.POST.get('action')
        property = get_object_or_404(Property, id=property_id)

        if action == 'delete':
            property.delete()
        elif action == 'edit':
            return redirect(reverse('edit_property', kwargs={'property_id': property_id}))
        
    return render(request, 'manage_properties.html', {'properties': properties})

def edit_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        property.title = request.POST.get('title')
        property.description = request.POST.get('description')
        property.address = request.POST.get('address')
        property.rent_amount = request.POST.get('rent_amount')

        if 'image' in request.FILES:
            property.image = request.FILES['image']

        property.is_approved = False
        property.save()
        return redirect('manage_properties')

    return render(request, 'edit_property.html', {'property': property})

@login_required
def list_properties(request):
    properties = Property.objects.filter(is_approved=True)

    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        return redirect(reverse('view_property', kwargs={'property_id': property_id}))
    
    return render(request, 'list_properties.html', {'properties': properties})

@login_required
def view_properties(request, property_id):
    tenant = request.user
    property = get_object_or_404(Property, id=property_id)
    today_date = date.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        rental_period = request.POST.get('rental_period')
        duration = int(request.POST.get('duration'))
        start_date = request.POST.get('start_date')
        aadhar = request.POST.get('aadhar')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        if rental_period == "days":
            end_date = start_date + timedelta(days=duration)
        elif rental_period == "months":
            end_date = start_date + relativedelta(months=duration)
        elif rental_period == "years":
            end_date = start_date + relativedelta(years=duration)
        
        existing_request = UserRequest.objects.filter(
            tenant=tenant,
            property=property,
            start_date=start_date,
            end_date=end_date,
            is_approved=False
            ).exists()
        
        if existing_request:
            error = 'Similar Request already exists'
            return render(request, 'view_property.html', {'property': property, 'today_date': today_date, 'error': error, 'tenant': tenant})
        else:
            UserRequest.objects.create(tenant = request.user, 
                                   property = property, 
                                   rental_period=rental_period,
                                   start_date = start_date,
                                   duration = duration,
                                   end_date = end_date,
                                   aadhar = aadhar,
                                   is_approved = False)
            return redirect('tenant_index')
            

    return render(request, 'view_property.html', {'property': property, 'today_date': today_date, 'tenant': tenant})

@login_required
def provider_update(request):
    provider = request.user

    try:
        term = Terms.objects.get(provider=provider)
    except Terms.DoesNotExist:
        term = None

    if request.method == "POST":
        terms_content = request.FILES.get('terms')
        if term:
            # Update existing terms
            term.terms = terms_content
            term.save()
            message = 'Your Terms Have Been Updated.'
        else:
            # Create new terms
            Terms.objects.create(provider=provider, terms=terms_content)
            message = 'Your Terms Have Been Created.'

        return render(request, 'provider_update.html', {'success': message, 'term': term})

    return render(request, 'provider_update.html', {'term': term})

@login_required
def tenant_requests(request):
    user_requests = UserRequest.objects.filter(tenant=request.user)
    return render(request, 'tenant_requests.html', {'user_requests': user_requests})

@login_required
def user_requests(request):
    provider_properties = Property.objects.filter(provider=request.user)
    user_requests = UserRequest.objects.filter(property__in=provider_properties, is_approved=False)

    if request.method == 'POST':
        request_id = request.POST.get('requests_id')
        action = request.POST.get('action')
        requests = get_object_or_404(UserRequest, id=request_id)

        if action == 'approve':
            requests.is_approved = True
            requests.save()
        elif action == 'reject':
            requests.delete()
    return render(request, 'user_requests.html', {'user_requests': user_requests})

@login_required
def payment_requests(request):
    requests = UserRequest.objects.filter(tenant=request.user, is_approved=True)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        request = get_object_or_404(UserRequest, id=request_id)

        if action == 'pay_deposit':
            return redirect('deposit_form', request_id = request.id)
        elif action == 'cancel':
            request.delete()
    return render(request, 'payment_requests.html', {'requests': requests})

@login_required
def deposit_form(request, request_id):

    user_request_instance = get_object_or_404(UserRequest, id=request_id)
    property_obj = user_request_instance.property
    try:
        terms = Terms.objects.get(provider=property_obj.provider)
    except Terms.DoesNotExist:
        terms = None
        
    deposit_amount = property_obj.rent_amount * Decimal('0.3')

    start_date = user_request_instance.start_date
    end_date = user_request_instance.end_date
    number_of_days = (end_date - start_date).days

    rent_per_day = property_obj.rent_amount
    amount = rent_per_day * number_of_days

    if number_of_days < 1:
        number_of_days = 1

    if request.method == 'POST':
        action = request.POST.get('action')
        card_number = request.POST.get('card_number')
        cvv = request.POST.get('cvv')

        if action == 'pay':
            agreement = RentalAgreement(
                tenant=request.user,
                property=property_obj,
                start_date=start_date,
                end_date=end_date,
                deposit_amount=deposit_amount,
                terms=terms.terms
            )
            agreement.save()

            Payment.objects.create(
                agreement=agreement,
                amount=amount,
                due_date=end_date,
                payment_date=date.today(),
                status='Pending'
            )

            user_request_instance.delete()

        return redirect('payment_success') 

    return render(request, 'deposit_form.html', {
        'user_request': user_request_instance,
        'property': property_obj,
        'terms': terms,
        'deposit_amount': deposit_amount,
    })

def payment_success(request):
    return render(request, 'payment_success.html')