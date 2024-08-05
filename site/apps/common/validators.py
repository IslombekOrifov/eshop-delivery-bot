from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r'^\+998\d{9}$',
    message='Invalid phone number format. It should start with +998 followed by 9 digits.',
    code='invalid_phone_number'
)