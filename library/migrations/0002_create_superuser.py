# Generated by Django 5.2 on 2025-04-15 12:01

from django.db import migrations
import os
from django.conf import settings
# Import make_password for hashing
from django.contrib.auth.hashers import make_password

# Function to create the superuser
def create_superuser(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    db_alias = schema_editor.connection.alias

    username = 'admin'
    password = 'admin' # Plain text password
    email = 'admin@example.com'

    if not User.objects.using(db_alias).filter(username=username).exists():
        print(f'\nCreating superuser: {username}')
        # Create user instance
        user = User(username=username,
                  email=email,
                  first_name='Default',
                  last_name='Admin',
                  is_staff=True,
                  is_superuser=True,
                  is_active=True,
                  role='admin')
        # Hash the password using make_password and assign it directly
        user.password = make_password(password)
        user.save(using=db_alias)
        print(f'Superuser {username} created successfully.')
    else:
        print(f'\nSuperuser {username} already exists.')

# Function to remove the superuser (optional, for reversing the migration)
def remove_superuser(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    db_alias = schema_editor.connection.alias
    username = 'admin'
    try:
        user = User.objects.using(db_alias).get(username=username)
        if user.is_superuser:
            print(f'\nDeleting superuser: {username}')
            user.delete()
            print(f'Superuser {username} deleted.')
        else:
            print(f'\nUser {username} exists but is not a superuser. Not deleted.')
    except User.DoesNotExist:
        print(f'\nSuperuser {username} does not exist. No action taken.')


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser, reverse_code=remove_superuser),
    ]
