from django.core.exceptions import ValidationError


def validate_positive_integer(value: int) -> None:
    if value <= 0:
        raise ValidationError("Value must be greater than zero.")