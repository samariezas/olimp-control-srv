from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Count, Q
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .models import Location, Computer, Task, Ticket
from .forms import NewTaskForm


@login_required
def index(request):
    current_time = timezone.now()
    ordered_computer_queryset = (
        Computer.objects
        .with_online_status()
        .order_by("sequence_num")
    )
    locations = Location.objects.order_by("sequence_num").prefetch_related(Prefetch(
        "computer_set",
        queryset=ordered_computer_queryset
    ))
    unassigned_computers = ordered_computer_queryset.filter(location=None)
    context = {
        "current_time": current_time,
        "locations": locations,
        "unassigned_computers": unassigned_computers,
    }
    return HttpResponse(render(request, "ctrl/index.html", context))


@login_required
def computer(request, machine_id):
    computer = get_object_or_404(Computer.objects.with_last_checkin(), machine_id=machine_id)
    checkins = computer.checkin_set.order_by("-timestamp")[:10]
    tickets = computer.ticket_set.order_by("-added")

    context = {
        "computer": computer,
        "checkins": checkins,
        "tickets": tickets,
    }
    return HttpResponse(render(request, "ctrl/computer.html", context))


@login_required
def task(request, pk):
    task = Task.annotate_counts(Task.objects).get(pk=pk)
    tickets = task.ticket_set.order_by("-pk")
    context = {
        "task": task,
        "tickets": tickets,
    }
    return HttpResponse(render(request, "ctrl/task.html", context))


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

    return render(request, "ctrl/create_task.html", {"form": form})


class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = "ctrl/task_list.html"
    context_object_name = "task_list"

    def get_queryset(self):
        return Task.annotate_counts(
            Task.objects.order_by("-added")
        )


class TicketView(LoginRequiredMixin, generic.DetailView):
    template_name = "ctrl/ticket.html"
    model = Ticket
