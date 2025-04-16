# Generated by Django 5.2 on 2025-04-15 10:45

from django.db import migrations
from decimal import Decimal

# Function to create default ReaderType entries
def create_reader_types(apps, schema_editor):
    ReaderType = apps.get_model('library', 'ReaderType')
    db_alias = schema_editor.connection.alias

    default_types = {
        'Обычный читатель': {
            'max_books_allowed': 5,
            'loan_period_days': 14,
            'can_use_reading_room': True,
            'can_use_loan': True,
            'fine_per_day': Decimal('10.00'),
        },
        'Сотрудник': {
            'max_books_allowed': 10, # Example: Staff might borrow more
            'loan_period_days': 30,
            'can_use_reading_room': True,
            'can_use_loan': True,
            'fine_per_day': Decimal('5.00'), # Lower fine for staff?
        },
        'Администратор': {
            'max_books_allowed': 15, # Example
            'loan_period_days': 60,
            'can_use_reading_room': True,
            'can_use_loan': True,
            'fine_per_day': Decimal('0.00'), # No fines for admin?
        },
        # Add other essential types if needed, e.g., 'Студент', 'Преподаватель'
        'Студент': {
            'max_books_allowed': 7,
            'loan_period_days': 21,
            'can_use_reading_room': True,
            'can_use_loan': True,
            'fine_per_day': Decimal('10.00'),
        },
         'Преподаватель': {
            'max_books_allowed': 10,
            'loan_period_days': 45,
            'can_use_reading_room': True,
            'can_use_loan': True,
            'fine_per_day': Decimal('5.00'),
        },
        # Types for Temporary Readers (cannot use loan)
        'Слушатель ФПК': {
            'max_books_allowed': 3, # Example limit for reading room
            'loan_period_days': 0, # Cannot take loan
            'can_use_reading_room': True,
            'can_use_loan': False,
            'fine_per_day': Decimal('15.00'), # Higher fine if somehow they get a book overdue?
        },
        'Абитуриент': {
            'max_books_allowed': 3,
            'loan_period_days': 0,
            'can_use_reading_room': True,
            'can_use_loan': False,
            'fine_per_day': Decimal('15.00'),
        },
        'Стажер': {
            'max_books_allowed': 5,
            'loan_period_days': 0,
            'can_use_reading_room': True,
            'can_use_loan': False,
            'fine_per_day': Decimal('15.00'),
        },
    }

    for type_name, defaults in default_types.items():
        if not ReaderType.objects.using(db_alias).filter(type_name=type_name).exists():
            print(f'\nCreating ReaderType: {type_name}')
            ReaderType.objects.using(db_alias).create(
                type_name=type_name,
                max_books_allowed=defaults['max_books_allowed'],
                loan_period_days=defaults['loan_period_days'],
                can_use_reading_room=defaults['can_use_reading_room'],
                can_use_loan=defaults['can_use_loan'],
                fine_per_day=defaults.get('fine_per_day', Decimal('10.00')) # Get fine or default
            )
        else:
            # Optionally update existing types if needed
            # reader_type = ReaderType.objects.using(db_alias).get(type_name=type_name)
            # if 'fine_per_day' in defaults and reader_type.fine_per_day != defaults['fine_per_day']:
            #     reader_type.fine_per_day = defaults['fine_per_day']
            #     reader_type.save(using=db_alias)
            #     print(f'\nUpdated fine_per_day for ReaderType: {type_name}')
            print(f'\nReaderType {type_name} already exists.')

# Optional: Add reverse code to delete these types if needed
def remove_reader_types(apps, schema_editor):
    ReaderType = apps.get_model('library', 'ReaderType')
    db_alias = schema_editor.connection.alias
    type_names = list(default_types.keys()) # Get all keys defined above
    print(f"\nAttempting to delete default reader types: { ', '.join(type_names)}")
    ReaderType.objects.using(db_alias).filter(type_name__in=type_names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_create_superuser'), # Runs after superuser creation
        # Ensure this runs before the migration adding the fine_per_day field if separate
        # Or adjust dependencies if fine_per_day was added in 0001_initial
    ]

    operations = [
        migrations.RunPython(create_reader_types, reverse_code=remove_reader_types),
    ]
