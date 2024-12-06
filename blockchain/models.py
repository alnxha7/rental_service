from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class User(AbstractUser):
    USER_ROLES = [
        ('tenant', 'Tenant'),
        ('provider', 'Provider')
    ]
    role = models.CharField(max_length=10, choices=USER_ROLES)
    verification_status = models.BooleanField(default=False)  # For Admin to verify accounts
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    document = models.ImageField(upload_to='documents/') 

    def __str__(self):
        return f"{self.email} ({self.role})"
    
class Property(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'provider'})
    title = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)  
    image = models.ImageField(upload_to='property_image/')

    def __str__(self):
        return f"{self.title} - {self.rent_amount}"
    
class Terms(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'provider'})
    terms = models.TextField()
    
class UserRequest(models.Model):
    RENTAL_PERIOD_CHOICES = [
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    rental_period = models.CharField(max_length=10, choices=RENTAL_PERIOD_CHOICES)
    duration = models.PositiveIntegerField()  # The number of days, months, or years
    aadhar = models.ImageField(upload_to='request_aadhar/')
    is_approved = models.BooleanField(default=False)
    monthly_rent = models.BooleanField(default=False)
    loan = models.BooleanField(default=False)
    loan_paid = models.BooleanField(default=False)

    def calculate_end_date(self):
        """
        Calculate and set the end_date based on rental_period and duration.
        """
        if self.rental_period == "days":
            self.end_date = self.start_date + timedelta(days=self.duration)
        elif self.rental_period == "months":
            self.end_date = self.start_date + relativedelta(months=self.duration)
        elif self.rental_period == "years":
            self.end_date = self.start_date + relativedelta(years=self.duration)
        self.save()

    def save(self, *args, **kwargs):
        # Automatically calculate end_date before saving
        if not self.end_date:
            self.calculate_end_date()
        super(UserRequest, self).save(*args, **kwargs)

class RentalAgreement(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    terms = models.TextField()  
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return f"Agreement for {self.property.title} with {self.tenant.username}"
    
class Payment(models.Model):
    agreement = models.ForeignKey(RentalAgreement, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')])

    def __str__(self):
        return f"Payment for {self.agreement.property.title} on {self.due_date}"


class MonthlyPayment(models.Model):
    request = models.ForeignKey(UserRequest, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    is_paid = models.BooleanField(default=False)

class LoanPay(models.Model):
    request = models.ForeignKey(UserRequest, on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    is_paid = models.BooleanField(default=False)

class MaintenanceRequest(models.Model):
    agreement = models.ForeignKey(RentalAgreement, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'provider'})
    description = models.TextField()
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')])
    resolved_date = models.DateField(null=True, blank=True)
    provider_comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Maintenance request for {self.agreement.property.title} - {self.status}"

