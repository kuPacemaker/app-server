# Generated by Django 3.1.1 on 2020-10-12 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20201012_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qapair',
            name='question',
            field=models.CharField(max_length=150),
        ),
    ]
