from datetime import datetime
from django.db.models import Model, CharField, TextField, DateTimeField

class Job(Model):
    name = CharField(max_length = 100, blank=False)
    args = TextField()
    kwargs = TextField()
    scheduled = DateTimeField(null = True, blank = True, 
        help_text = "If not set, will be executed ASAP")
    executed = DateTimeField(null = True, blank = True)

    def __unicode__(self):
        return self.name

    @classmethod
    def next_job(cls):
        now = datetime.now()
        remaining_job = Job.objects.filter(executed__isnull = True, scheduled__lt=now)
        return None if not remaining_job else remaining_job[0] 

    class Meta:
        ordering = ['id']
 
