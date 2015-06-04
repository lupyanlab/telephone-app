# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grunt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='parent',
            field=models.ForeignKey(blank=True, to='grunt.Message', null=True),
            preserve_default=True,
        ),
    ]
