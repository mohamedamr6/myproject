"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import index, register, edit_replica_set, delete_replica_set, list_pods, create_pods, delete_deployment, edit_pod, edit_deployment, delete_pod, apply_yaml_view, list_namespaces, create_namespaces, list_deployments, list_replica_sets, list_workloads

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', index , name='index'),
    path('register', register, name='register' ),
    path('list-pods/', list_pods, name='list_pods'),
    path('create-pods/', create_pods, name='create_pods'),
    path('edit_pod/<str:namespace>/<str:name>/', edit_pod, name='edit_pod'),
    path('edit_replica_set/<str:namespace>/<str:name>/', edit_replica_set, name='edit_replica_set'),
    path('edit_deployment/<str:namespace>/<str:name>/', edit_deployment, name='edit_deployment'),
    path('delete_pod/<str:namespace>/<str:name>/', delete_pod, name='delete_pod'),
    path('delete_replica_set/<str:namespace>/<str:name>/', delete_replica_set, name='delete_replica_set'),
    path('delete_deployment/<str:namespace>/<str:name>/', delete_deployment, name='delete_deployment'),
    path('apply_yaml/', apply_yaml_view, name='apply_yaml'),
    path('list-namespaces/', list_namespaces, name='list_namespaces'),
    path('create-namespaces/', create_namespaces, name='create_namespaces'),
    path('list-deployments/', list_deployments, name='list_deployments'),
    path('list-replica_sets/', list_replica_sets, name='list_replica_sets'),
    path('list-workloads/', list_workloads, name='list_workloads'),
]


