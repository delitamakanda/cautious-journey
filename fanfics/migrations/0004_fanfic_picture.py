# Generated by Django 2.2.13 on 2021-04-12 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fanfics', '0003_fanfic_link_fanfic'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanfic',
            name='picture',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
