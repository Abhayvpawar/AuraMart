# Generated by Django 5.1.5 on 2025-02-26 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('E_Commerce', '0004_rename_emai_userinfo_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userinfo',
            name='user',
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='email',
            field=models.CharField(max_length=255),
        ),
    ]
