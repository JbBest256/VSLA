# Generated by Django 5.0.6 on 2024-10-19 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_alter_accountsettings_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='accountsettings',
            unique_together={('name', 'financial_year')},
        ),
        migrations.RemoveField(
            model_name='accountsettings',
            name='association',
        ),
    ]
