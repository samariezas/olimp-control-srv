from django.db import models
from django.db.models import Count, Q
from django.contrib.auth.models import User


class Location(models.Model):
    name = models.TextField()

    def __str__(self):
        return f"{self.name}"


class Computer(models.Model):
    machine_id = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=32)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def most_recent_checkin(self):
        cs = self.checkin_set.order_by("-timestamp")[:1]
        return cs[0] if cs else None

    @property
    def rooted(self):
        c = self.most_recent_checkin
        return c.has_root if c else False

    def __str__(self):
        return f"{self.name} ({self.machine_id})"


class CheckIn(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    pseudo_timestamp = models.BigIntegerField(default=0)
    uptime = models.CharField(max_length=100, default="")
    has_root = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.computer.name} @ {self.timestamp}"


class UnknownComputer(models.Model):
    machine_id = models.CharField(max_length=40)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.machine_id}"


class Task(models.Model):
    name = models.TextField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    added = models.DateTimeField(auto_now_add=True)
    run_as = models.CharField(max_length=16)
    payload = models.TextField()


    @staticmethod
    def q_tickets_new():
        return Q(ticket__fetched__isnull=True)

    @staticmethod
    def q_tickets_in_progress():
        return Q(ticket__fetched__isnull=False, ticket__completed__isnull=True)

    @staticmethod
    def q_tickets_completed():
        return Q(ticket__completed__isnull=False)

    @staticmethod
    def q_tickets_error():
        return Q(~Q(ticket__exit_code=0), ticket__completed__isnull=False)

    @staticmethod
    def annotate_counts(obj):
        return obj.annotate(
            new_count=Count("ticket", filter=Q(ticket__fetched__isnull=True)),
            in_progress_count=Count("ticket", filter=Q(ticket__fetched__isnull=False, ticket__completed__isnull=True)),
            completed_count=Count("ticket", filter=Q(ticket__completed__isnull=False)),
            error_count=Count("ticket", filter=Q(~Q(ticket__exit_code=0), ticket__completed__isnull=False)),
        )

    def __str__(self):
        return f"{self.name}"


class Ticket(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    fetched = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    runtime = models.FloatField(null=True, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    stdout = models.TextField(blank=True, default="")
    stderr = models.TextField(blank=True, default="")

    @property
    def is_new(self):
        return self.fetched is None

    @property
    def is_completed(self):
        return self.completed != None

    @property
    def is_in_progress(self):
        return not (self.is_new or self.is_completed)

    @property
    def status_string(self):
        if self.is_new:
            return 'new'
        elif self.is_completed:
            return 'done'
        elif self.is_in_progress:
            return 'in progress'
        else:
            return 'unknown'

    @property
    def runtime_rounded(self):
        return f'{self.runtime:.3f}s'

    def __str__(self):
        return f"{self.task.pk} @ {self.computer.name}"
