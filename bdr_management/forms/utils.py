from django.forms import ModelChoiceField


def set_empty_label(fields, empty_label):
    for field_name in fields:
        field = fields[field_name]
        if isinstance(field, ModelChoiceField):
            field.empty_label = empty_label