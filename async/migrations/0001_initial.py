# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('executed', models.DateTimeField(auto_now_add=True)),
                ('exception', models.TextField()),
                ('traceback', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reference', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('args', models.TextField()),
                ('kwargs', models.TextField()),
                ('meta', models.TextField()),
                ('result', models.TextField(blank=True)),
                ('priority', models.IntegerField()),
                ('identity', models.CharField(max_length=100, db_index=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('scheduled', models.DateTimeField(help_text=b'If not set, will be executed ASAP', null=True, blank=True)),
                ('started', models.DateTimeField(null=True, blank=True)),
                ('executed', models.DateTimeField(null=True, blank=True)),
                ('cancelled', models.DateTimeField(null=True, blank=True)),
                ('group', models.ForeignKey(related_name='jobs', blank=True, to='async.Group', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='group',
            name='final',
            field=models.ForeignKey(related_name='ends', blank=True, to='async.Job', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='error',
            name='job',
            field=models.ForeignKey(related_name='errors', to='async.Job'),
            preserve_default=True,
        ),
    ]
