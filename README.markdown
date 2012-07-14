Django Async is an asynchronous execution queue for Django with proper database transaction management.

Building a database backed task queue is a fairly trivial thing, but getting the database transactions exactly right is no simple matter.


# Using Django Async #

Installation is very simple, just add the `async` application to your Django applications in `settings.py`.

To run a job asynchronously just use the `schedule` function:

    from async import schedule
    schedule('my.function', args=(1, 2, 3), kwargs=dict(key='value'))

Tasks can be run by executing the management command `flush_queue`:

    python manage.py flush_queue

`flush_queue` will run once through the jobs that are scheduled to run at that time, but will exit early if any job throws an exception. Normally you would use it from an external script that simply keeps re-running the command.

    while [ true ] ; do ( python manage.py flush_queue && sleep 10 ) ; done

Jobs are executed in priority order first (higher numbers execute earlier), then by the scheduled time (unscheduled jobs will go last, but of course only jobs whose scheduled time has arrived will run) and finally by their ID order (which should be the order they were added). A failed task will be re-scheduled for later execution.

##`async.schedule`##

    schedule(function, args = None, kwargs = None, run_after= None, meta = None, priority = 5)

Returns a Job instance that is used to record the task in the database. The job has a method `execute` which will attempt to run the job. **Don't do this directly until you've fully understood how transactions are handled**

* _function_ Either the fully qualified name of the function that is to be run, or the function itself.
* _args_ A tuple or list of arguments to be given to the function.
* _kwargs_ A dict containing key word arguments to be passed to the function.
* _run_after_ The earliest time that the function should be run.
* _meta_ Parameters for controlling how the function is to be executed.
* _priority_ Jobs with higher numbers are always executed before jobs with lower numbers.

##`async.api.deschedule`##

    deschedule(function, args = None, kwargs = None)

Marks all jobs in the queue that match the given function _and arguments_ as executed.

De-scheduling does not guarantee that the de-scheduled tasks will never run unless the de-scheduling is done within a task executed in the job queue. This is because the task might have already started executing within the queue whilst it is de-scheduled from outside the queue.

##`async.api.health`##

    info = health()

Returns a `dict` containing basic information about the queue which can be used for monitoring.


# Transaction handling #

Database transactions are hard to get right, and unfortunately Django doesn't make them much easier. Firstly, you really want to be using a proper transactional database system.

Django has two major flaws when it comes to transaction handling:

1. The Django transaction functionality fails to create composable transactions.
2. The [https://docs.djangoproject.com/en/dev/topics/db/transactions/](Django documentation) makes a very poor recommendation about where to put the `django.middleware.transaction.TransactionMiddleware`.

The first problem is not going to get fixed in Django, but the second can be handled by putting the middleware in the right place -- that is, as early as possible. The only middleware that should run before the transaction middleware is any whose functionality relies on it being first.

Within the async task execution each task is executed decorated by `django.db.transaction.commit_on_success`. _This means that you cannot execute a task directly from within a page request if you are using the transaction middleware._


# Doing development #

_This project uses git flow. Don't forget to do `git flow init -d`_

To create virtual environments for running the tests you can execute `test-projects/make-virtual-environments`. To run the tests execute `runtests`.
