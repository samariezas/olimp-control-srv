from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Count, Q
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views import generic
from django.utils import timezone

from .models import Location, Computer, Task, Ticket


@login_required
def index(request):
    current_time = timezone.now()
    locations = Location.objects.order_by("pk").prefetch_related(Prefetch(
        "computer_set",
        queryset=Computer.objects.order_by("name")
    ))
    unassigned_computers = Computer.objects.order_by("name").filter(location=None)
    context = {
        "current_time": current_time,
        "locations": locations,
        "unassigned_computers": unassigned_computers,
    }
    return HttpResponse(render(request, "ctrl/index.html", context))


@login_required
def computer(request, machine_id):
    computer = get_object_or_404(Computer, machine_id=machine_id)
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
