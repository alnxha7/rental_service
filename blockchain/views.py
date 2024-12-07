from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Property, Terms, RentalAgreement, UserRequest, Payment, MonthlyPayment, LoanPay, MaintenanceRequest
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
        elif action == "remove":
            user.delete()
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

            month_existing_request = UserRequest.objects.filter(
                tenant=tenant,
                property=property,
                start_date=start_date,
                end_date=end_date,
                is_approved=False
            ).exists()

            if month_existing_request:
                error = 'A similar request already exists.'
                return render(request, 'view_property.html', {
                    'property': property,
                    'today_date': today_date,
                    'error': error,
                    'tenant': tenant
                })

            # Create a UserRequest entry
            monthly_request = UserRequest.objects.create(
                tenant=request.user,
                property=property,
                rental_period=rental_period,
                start_date=start_date,
                duration=duration,
                end_date=end_date,
                aadhar=aadhar,
                is_approved=False,
                monthly_rent=True
            )

            monthly_amount = property.rent_amount * 30

            # Create multiple MonthlyPayment entries
            for i in range(duration):
                due_date = start_date + relativedelta(months=i)  # Increment by month
                MonthlyPayment.objects.create(
                    request=monthly_request,
                    tenant=request.user,
                    property=property,
                    due_date=due_date,
                    amount=monthly_amount,
                    is_paid=False
                )

            return redirect('tenant_index')
        
        
        elif rental_period == "years":
            end_date = start_date + relativedelta(years=duration)

            year_request = UserRequest.objects.filter(
            tenant=tenant,
            property=property,
            start_date=start_date,
            end_date=end_date,
            is_approved=False
            ).exists()
        
            if year_request:
                error = 'Similar Request already exists'
                return render(request, 'view_property.html', {'property': property, 'today_date': today_date, 'error': error, 'tenant': tenant})
            else:
                loan = UserRequest.objects.create(tenant = request.user, 
                                   property = property, 
                                   rental_period=rental_period,
                                   start_date = start_date,
                                   duration = duration,
                                   end_date = end_date,
                                   aadhar = aadhar,
                                   is_approved = False,
                                   loan=True)
                
                loan_amount = property.rent_amount * 30 * 12

                try:
                    loan_pay = LoanPay.objects.create(
                    request=loan,
                    tenant=request.user,
                    property=property,
                    due_date=end_date,
                    amount=loan_amount,
                    is_paid=False
                    )
                    print(f"LoanPay created successfully: {loan_pay}")
                except Exception as e:
                     print(f"Error creating LoanPay: {e}")
            
                return redirect('tenant_index')

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
        terms_content = request.POST.get('terms')
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
    user_requests = UserRequest.objects.filter(tenant=request.user, monthly_rent=False)
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
    user_requests = UserRequest.objects.filter(tenant=request.user, is_approved=True, monthly_rent=False, loan=False)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        user_request = get_object_or_404(UserRequest, id=request_id)

        if action == 'pay_deposit':
            return redirect('deposit_form', request_id = user_request.id)
        elif action == 'cancel':
            user_request.delete()
    return render(request, 'payment_requests.html', {'requests': user_requests})

@login_required
def deposit_form(request, request_id):

    user_request_instance = get_object_or_404(UserRequest, id=request_id)
    property_obj = user_request_instance.property

    try:
        terms = Terms.objects.get(provider=property_obj.provider)
    except Terms.DoesNotExist:
        terms = None
     
    if user_request_instance.loan:  # If it's a loan
        deposit_amount = property_obj.rent_amount * Decimal(30) * Decimal(12)
    else:  # Normal calculation
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

            if not user_request_instance.loan:

                Payment.objects.create(
                    agreement=agreement,
                    amount=amount,
                    due_date=end_date,
                    payment_date=date.today(),
                    status='Pending'
                 )

                user_request_instance.delete()

                reciept = {
                    'tenant_name': request.user.username,
                    'provider_name': property_obj.provider.username,
                    'property': property_obj.title,
                    'amount': amount,
                    'end_date': end_date,
                    'payment_date': date.today()
                }

                return render(request, 'payment_success.html', reciept) 
            
            else:
                user_request_instance.loan_paid=True
                user_request_instance.save()

                loan = get_object_or_404(LoanPay, request=user_request_instance)
                loan.is_paid=True
                loan.save()
                reciept = {
                    'tenant_name': request.user.username,
                    'provider_name': property_obj.provider.username,
                    'property': property_obj.title,
                    'amount': amount,
                    'end_date': end_date,
                    'payment_date': date.today()
                }
                return render(request, 'payment_success.html', reciept) 
        

    return render(request, 'deposit_form.html', {
        'user_request': user_request_instance,
        'property': property_obj,
        'terms': terms,
        'deposit_amount': deposit_amount,
    })

def payment_success(request):
    return render(request, 'payment_success.html')

def monthly_payment(request):
    requests = MonthlyPayment.objects.filter(tenant=request.user)

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        user_request = get_object_or_404(MonthlyPayment,id=request_id)

        if action == 'pay':
            return redirect('pay_monthly', request_id=user_request.id)
        if action == 'cancel':
            user_request.delete()

    return render(request, 'monthly_payment.html', {'requests': requests})

def pay_monthly(request, request_id):
    user_request = get_object_or_404(MonthlyPayment,id=request_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        start_date = user_request.request.start_date
        end_date = user_request.request.end_date
        deposit_amount = user_request.amount
        property = user_request.property
        tenant = request.user
        provider = user_request.property.provider
        terms = get_object_or_404(Terms, provider=provider)

        if action == 'pay':
            user_request.is_paid = True
            user_request.save()
            RentalAgreement.objects.create(tenant=tenant,
                                           property=property,
                                           start_date=start_date,
                                           end_date=end_date,
                                           deposit_amount=deposit_amount,
                                           terms=terms)
            return redirect('payment_success')
    return render(request, 'pay_monthly.html', { 'user_request': user_request })

def provider_monthly(request):
    provider_properties = Property.objects.filter(provider=request.user)
    user_requests = MonthlyPayment.objects.filter(property__in=provider_properties)
    return render(request, 'provider_monthly.html', {'user_requests': user_requests})

def provider_loan(request):
    provider_properties = Property.objects.filter(provider=request.user)
    user_requests = LoanPay.objects.filter(property__in=provider_properties)
    return render(request, 'provider_loan.html', {'user_requests': user_requests})

def monthly_request(request):
    user_requests = UserRequest.objects.filter(tenant=request.user, is_approved=True, monthly_rent=True)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        user_request = get_object_or_404(UserRequest, id=request_id)

        if action == 'pay_deposit':
            return redirect('deposit_form', request_id = user_request.id)
        elif action == 'cancel':
            user_request.delete()
    return render(request, 'monthly_request.html', {'user_requests': user_requests})

def loan_requests(request):
    user_requests = UserRequest.objects.filter(tenant=request.user, is_approved=True, loan=True, loan_paid=False)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        user_request = get_object_or_404(UserRequest, id=request_id)

        if action == 'pay_deposit':
            return redirect('deposit_form', request_id = user_request.id)
        elif action == 'cancel':
            user_request.delete()
    return render(request, 'loan_requests.html', {'user_requests': user_requests})

def tenant_maintenance(request):
    properties = RentalAgreement.objects.filter(tenant=request.user,
                                                is_active=True)
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        agreement = get_object_or_404(RentalAgreement, id=property_id)
        description = request.POST.get('maintenance_request')
        provider = agreement.property.provider
        action = request.POST.get('action')
        if action == 'request':
            MaintenanceRequest.objects.create(agreement=agreement, description=description, status='pending', provider=provider)
  
    return render(request, 'tenant_maintenance.html', {'properties': properties})

def provider_maintenance(request):
    user_requests = MaintenanceRequest.objects.filter(provider=request.user)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action_choice = request.POST.get('action_choice')
        action = request.POST.get('action')
        additional_info = request.POST.get('additional_info')
        maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)

        if action == 'ok':
            if action_choice == 'in_progress':
                maintenance_request.provider_comments = additional_info
                maintenance_request.status = 'in_progress'
                maintenance_request.resolved_date = None
                maintenance_request.save()
            elif action_choice == 'completed':
                maintenance_request.provider_comments = additional_info
                maintenance_request.status = 'completed'
                maintenance_request.resolved_date = date.today()
                maintenance_request.save()
            elif action_choice == 'pending':
                maintenance_request.provider_comments = additional_info
                maintenance_request.status = 'pending'
                maintenance_request.resolved_date = None
                maintenance_request.save()

    return render(request, 'provider_maintenance.html', {'user_requests': user_requests})

def maintenance_status(request):
    tenant = request.user
    reports = MaintenanceRequest.objects.filter(agreement__tenant=tenant)
    return render(request, 'maintenance_status.html', {'reports': reports})

def tenant_history(request):
    histories = RentalAgreement.objects.filter(tenant=request.user)
    return render(request, 'tenant_history.html', {'histories': histories})

def provider_history(request):
    histories = Payment.objects.filter(agreement__property__provider=request.user)
    return render(request, 'provider_history.html', {'histories': histories})

def pay_remaining(request):
    payments = Payment.objects.filter(agreement__tenant=request.user)
    for payment in payments:
        payment.remaining_amount = (payment.amount) - (payment.agreement.property.rent_amount * Decimal('0.3'))

    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')

        if action == 'pay':
            return redirect('remaining_payment', payment_id=payment_id)
    return render(request, 'pay_remaining.html', {'payments': payments})

def remaning_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.remaining_amount = (payment.amount) - (payment.agreement.property.rent_amount * Decimal('0.3'))

    if request.method == 'POST':
        tenant_name = request.user.username
        provider_name = payment.agreement.property.provider.username
        property = payment.agreement.property
        amount = payment.remaining_amount
        end_date = payment.agreement.end_date
        payment_date = date.today()

        payment.status = "Paid"
        payment.save()

        context = {'tenant_name': tenant_name,
                   'provider_name': provider_name,
                   'property': property, 
                   'amount': amount,
                   'end_date': end_date, 
                   'payment_date': payment_date}
        
        return render(request, 'payment_success.html', context)
    return render(request, 'remaining_payment.html', {'payment': payment})

