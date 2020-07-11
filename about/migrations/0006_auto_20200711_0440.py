# Generated by Django 2.2.7 on 2020-07-11 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('about', '0005_auto_20200711_0409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='check_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='application',
            name='first_pennapps',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='application',
            name='num_graders',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=1),
        ),
        migrations.AlterField(
            model_name='application',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=2),
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(default='N/A', max_length=30),
        ),
    ]
