# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import grunt.handlers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('selection_method', models.CharField(default=b'YNG', max_length=3, choices=[(b'YNG', b'youngest'), (b'RND', b'random')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, null=True, blank=True)),
                ('chain_order', models.CharField(default=b'SEQ', max_length=3, choices=[(b'SEQ', b'sequential'), (b'RND', b'random')])),
                ('status', models.CharField(default=b'ACTIV', max_length=5, choices=[(b'ACTIV', b'active'), (b'INACT', b'inactive')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, blank=True)),
                ('generation', models.IntegerField(default=0, editable=False)),
                ('audio', models.FileField(upload_to=grunt.handlers.message_path, blank=True)),
                ('chain', models.ForeignKey(to='grunt.Chain')),
                ('parent', models.ForeignKey(blank=True, to='grunt.Message', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='chain',
            name='game',
            field=models.ForeignKey(to='grunt.Game'),
            preserve_default=True,
        ),
    ]
