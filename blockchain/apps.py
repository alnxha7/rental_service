from django.apps import AppConfig


class BlockchainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blockchain'

    def ready(self):
        from .models import RentalAgreement
        from django.utils.timezone import now
        expired_agreements = RentalAgreement.objects.filter(end_date__lt=now().date(), is_active=True)
        expired_agreements.update(is_active=False)