"""Add uid field to Order model."""
import random

from django.db import migrations, models


def fill_existing_uids(apps, schema_editor):
    """Fill uid for existing orders."""
    Order = apps.get_model('orders', 'Order')
    used = set()
    for order in Order.objects.all():
        while True:
            uid = str(random.randint(100000, 999999))
            if uid not in used:
                used.add(uid)
                order.uid = uid
                order.save(update_fields=['uid'])
                break


def reverse_fill(apps, schema_editor):
    """Reverse migration - nothing to do."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_add_payment_method'),
    ]

    operations = [
        # Step 1: Add uid field as nullable
        migrations.AddField(
            model_name='order',
            name='uid',
            field=models.CharField(
                db_index=True,
                max_length=10,
                null=True,
                blank=True,
                verbose_name='Номер заказа',
            ),
        ),
        # Step 2: Fill existing orders with unique UIDs
        migrations.RunPython(fill_existing_uids, reverse_fill),
        # Step 3: Make uid non-nullable and unique
        migrations.AlterField(
            model_name='order',
            name='uid',
            field=models.CharField(
                db_index=True,
                max_length=10,
                unique=True,
                verbose_name='Номер заказа',
            ),
        ),
    ]
