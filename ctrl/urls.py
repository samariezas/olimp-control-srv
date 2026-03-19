from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="ctrl.index"),
    path("status-partial/", views.index_status_partial, name="ctrl.index_status_partial"),
    path("location/<int:pk>/", views.location_detail, name="ctrl.location"),
    path("location/<int:pk>/partial/", views.location_detail_partial, name="ctrl.location_partial"),
    path("computer/<str:machine_id>/", views.computer, name="ctrl.computer"),
    path("task_list/", views.TaskListView.as_view(), name="ctrl.task_list"),
    path("task/<int:pk>/", views.task, name="ctrl.task"),
    path("create-task/", views.create_task, name="ctrl.create_task"),
    path("ticket/<int:pk>/", views.TicketView.as_view(), name="ctrl.ticket"),
]
