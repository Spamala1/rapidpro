# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-15 16:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    INDEX_SQL = """
        CREATE INDEX CONCURRENTLY contacts_fields_idx ON contacts_contact USING GIN(fields);
    """

    dependencies = [
        ('contacts', '0073_backfill_contact_fields'),
    ]

    operations = [
        migrations.RunSQL(INDEX_SQL, "")
    ]
