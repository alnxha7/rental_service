# Generated by Django 5.1.3 on 2024-12-04 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0011_userrequest_loan_paid_userrequest_monthly_rent_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrequest',
            name='loan_paid',
        ),
        migrations.RemoveField(
            model_name='userrequest',
            name='monthly_rent_paid',
        ),
    ]