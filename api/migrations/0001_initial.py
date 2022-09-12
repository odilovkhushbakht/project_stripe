# Generated by Django 4.1.1 on 2022-09-11 11:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default='description')),
                ('price', models.IntegerField(default=0)),
                ('currency', models.CharField(default='usd', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_num', models.IntegerField(default=0)),
                ('quantity', models.IntegerField(default=1)),
                ('product_num', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.item')),
            ],
        ),
    ]
