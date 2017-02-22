# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Job'
        db.create_table('async_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('args', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.TextField')()),
            ('meta', self.gf('django.db.models.fields.TextField')()),
            ('result', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')()),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('scheduled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('executed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('async', ['Job'])

        # Adding model 'Error'
        db.create_table('async_error', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(related_name='errors', to=orm['async.Job'])),
            ('executed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('exception', self.gf('django.db.models.fields.TextField')()),
            ('traceback', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('async', ['Error'])


    def backwards(self, orm):
        # Deleting model 'Job'
        db.delete_table('async_job')

        # Deleting model 'Error'
        db.delete_table('async_error')


    models = {
        'async.error': {
            'Meta': {'object_name': 'Error'},
            'exception': ('django.db.models.fields.TextField', [], {}),
            'executed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'errors'", 'to': "orm['async.Job']"}),
            'traceback': ('django.db.models.fields.TextField', [], {})
        },
        'async.job': {
            'Meta': {'object_name': 'Job'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'args': ('django.db.models.fields.TextField', [], {}),
            'executed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'kwargs': ('django.db.models.fields.TextField', [], {}),
            'meta': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'priority': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['async']

