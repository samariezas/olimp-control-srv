from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q, Exists, OuterRef
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .models import Location, Computer, Task, Ticket
from .forms import NewTaskForm


def _computer_queryset():
    return (
        Computer.objects
        .with_online_status()
        .annotate(
            has_in_progress=Exists(
                Ticket.objects.filter(
                    computer=OuterRef("pk"),
                    fetched__isnull=False,
                    completed__isnull=True,
                )
            )
        )
        .order_by("sequence_num")
    )


def _get_status_context():
    ordered_computer_queryset = _computer_queryset()
    locations = list(Location.objects.order_by("sequence_num").prefetch_related(Prefetch(
        "computer_set",
        queryset=ordered_computer_queryset
    )))
    unassigned_computers = list(ordered_computer_queryset.filter(location=None))

    all_computers = [c for loc in locations for c in loc.computer_set.all()] + unassigned_computers
    online_count = sum(1 for c in all_computers if c.is_online)
    total_count = len(all_computers)

    return {
        "locations": locations,
        "unassigned_computers": unassigned_computers,
        "online_count": online_count,
        "offline_count": total_count - online_count,
        "total_count": total_count,
    }


@login_required
def index(request):
    return render(request, "ctrl/index.html", _get_status_context())


@login_required
def index_status_partial(request):
    return render(request, "ctrl/partial/index_status_partial.html", _get_status_context())


def _get_location_context(pk):
    location = get_object_or_404(Location, pk=pk)
    computers = list(_computer_queryset().filter(location=location))
    online_count = sum(1 for c in computers if c.is_online)
    return {
        "location": location,
        "computers": computers,
        "online_count": online_count,
        "offline_count": len(computers) - online_count,
        "total_count": len(computers),
    }


@login_required
def location_detail(request, pk):
    return render(request, "ctrl/location.html", _get_location_context(pk))


@login_required
def location_detail_partial(request, pk):
    return render(request, "ctrl/partial/location_partial.html", _get_location_context(pk))


@login_required
def computer(request, machine_id):
    computer = get_object_or_404(Computer.objects.with_last_checkin(), machine_id=machine_id)
    checkins = computer.checkin_set.order_by("-timestamp")[:10]
    tickets = computer.ticket_set.select_related("task").order_by("-added")

    context = {
        "computer": computer,
        "checkins": checkins,
        "tickets": tickets,
    }
    return render(request, "ctrl/computer.html", context)


@login_required
def task(request, pk):
    task = get_object_or_404(Task.objects.with_ticket_status_counts(), pk=pk)
    tickets = task.ticket_set.select_related("computer", "computer__location").order_by("-pk")
    context = {
        "task": task,
        "tickets": tickets,
    }
    return render(request, "ctrl/task.html", context)


@login_required
def create_task(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task_computers = form.cleaned_data["computers"]
            tickets = [Ticket(task=task, computer=computer)
                       for computer in task_computers]
            with transaction.atomic():
                task.save()
                Ticket.objects.bulk_create(tickets)
            return redirect("ctrl.task", pk=task.pk)
    else:
        form = NewTaskForm()

    computers_by_location = {}
    for c in form.fields["computers"].queryset.select_related("location"):
        loc_name = c.location.name if c.location else "Unassigned"
        computers_by_location.setdefault(loc_name, []).append(c)

    return render(request, "ctrl/create_task.html", {
        "form": form,
        "computers_by_location": computers_by_location,
    })


class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = "ctrl/task_list.html"
    context_object_name = "task_list"

    def get_queryset(self):
        return Task.objects.with_ticket_status_counts().select_related("author").order_by("-added")


class TicketView(LoginRequiredMixin, generic.DetailView):
    template_name = "ctrl/ticket.html"
    model = Ticket
