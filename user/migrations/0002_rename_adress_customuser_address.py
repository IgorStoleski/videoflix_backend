# Generated by Django 5.0.6 on 2024-05-30 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='adress',
            new_name='address',
        ),
    ]