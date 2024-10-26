# yourapp/validators.py
from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 4:
            raise ValidationError("Password must be at least 4 characters long.")
        if re.findall(r'[^\w]', password):
            raise ValidationError("Password cannot contain special characters.")

    def get_help_text(self):
        return "Your password must be at least 4 characters long and cannot contain special characters."
