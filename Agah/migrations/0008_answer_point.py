# Generated by Django 3.2.6 on 2021-08-10 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agah', '0007_auto_20210810_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='point',
            field=models.PositiveSmallIntegerField(default=0, editable=False, verbose_name='امتیاز'),
        ),
    ]