from django.db.models import Model, CharField, TextField, DateTimeField

class Job(Model):
    """Execute a Python function asynchronously.

    Do not create these objects directly.
    Use the function create to make them.
    """
    name = CharField(max_length = 100, blank=False)
    args = TextField()
    kwargs = TextField()

    scheduled = DateTimeField(
        help_text = "If not set, will be executed ASAP",
        null = True,
        blank = True
    )
    executed = DateTimeField(
        null = True,
        blank = True
    )

    def __unicode__(self):
        return self.name

    @classmethod
    def create(cls, function, *args, **kwargs):
        return cls(name = function.func_name, args = args, kwargs = kwargs)

    class Meta:
        ordering = ['-id']
 
