# Generated by Django 3.2.16 on 2023-09-28 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=35, unique=True, verbose_name='Цветовой код'),
        ),
    ]
