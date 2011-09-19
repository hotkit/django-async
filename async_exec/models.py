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

    class Meta:
        ordering = ['-id']
 
