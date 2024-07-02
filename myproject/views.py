# views.py
import logging
from django.http import JsonResponse
from django.shortcuts import render , redirect
from kubernetes import client, config, utils
from django.urls import reverse 
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User, auth
from django.contrib import messages
# from kubernetes import matplotlibpyplot as plt
from kubernetes.client.rest import ApiException
from .forms import CreatePodForm, CreateNamespaceForm
import yaml
import re

logger = logging.getLogger('myproject')

def index(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password =password  )

        if user is not None:
            auth.login(request , user)
            return redirect(reverse('list_deployments'))   
        else:
            messages.info(request, 'invalid username or password')
            return redirect("/")
    else:
        return render(request,'index.html')

def register(request):

    if request.method == 'POST':

        email = request.POST['email']
        username = request.POST['username']
        password= request.POST['password']


        user = User.objects.create_user(username = username , password = password , email = email)
        user.save()
        print('user created')
        return redirect(reverse('index'))   

    return render(request,'register.html')


def get_workload_status():
    # Load kubeconfig
    config.load_kube_config()

    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    # Get all namespaces
    namespaces = [ns.metadata.name for ns in v1.list_namespace().items]

    workload_status = {
        'pods': {'Running': 0, 'Pending': 0, 'Failed': 0, 'Unknown': 0},
        'deployments': {'Available': 0, 'Unavailable': 0}
    }

    # Get pod statuses
    for ns in namespaces:
        pods = v1.list_namespaced_pod(ns).items
        for pod in pods:
            phase = pod.status.phase
            if phase in workload_status['pods']:
                workload_status['pods'][phase] += 1
            else:
                workload_status['pods']['Unknown'] += 1

    # Get deployment statuses
    for ns in namespaces:
        deployments = apps_v1.list_namespaced_deployment(ns).items
        for deploy in deployments:
            if deploy.status.available_replicas == deploy.status.replicas:
                workload_status['deployments']['Available'] += 1
            else:
                workload_status['deployments']['Unavailable'] += 1

    return workload_status



def list_workloads(request):
    # Load the kubeconfig file (usually located at ~/.kube/config)
    config.load_kube_config()

    # Create instances of the necessary API classes
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()
    # Initialize dictionaries to store the workloads
    list_workloads = {
        "pods": [],
        "deployments": [],
        "statefulsets": [],
        "daemonsets": [],
        "replicasets": []
    }
    
    counts = {
        "pods": 0,
        "deployments": 0,
        "statefulsets": 0,
        "daemonsets": 0,
        "replicasets": 0
    }

    try:
        # List pods
        pods = core_v1.list_pod_for_all_namespaces().items
        counts["pods"] = len(pods)
        for pod in pods:
            list_workloads["pods"].append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace
            })        
        # List Deployments
        deployments = apps_v1.list_deployment_for_all_namespaces().items
        counts["deployments"] = len(deployments)
        for deployment in deployments:
            list_workloads["deployments"].append({
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace
            })

        # List StatefulSets
        statefulsets = apps_v1.list_stateful_set_for_all_namespaces().items
        counts["statefulsets"] = len(statefulsets)
        for statefulset in statefulsets:
            list_workloads["statefulsets"].append({
                "name": statefulset.metadata.name,
                "namespace": statefulset.metadata.namespace
            })

        # List DaemonSets
        daemonsets = apps_v1.list_daemon_set_for_all_namespaces().items
        counts["daemonsets"] = len(daemonsets)
        for daemonset in daemonsets:
            list_workloads["daemonsets"].append({
                "name": daemonset.metadata.name,
                "namespace": daemonset.metadata.namespace
            })

        # List ReplicaSets
        replicasets = apps_v1.list_replica_set_for_all_namespaces().items
        counts["replicasets"] = len(replicasets)
        for replicaset in replicasets:
            list_workloads["replicasets"].append({
                "name": replicaset.metadata.name,
                "namespace": replicaset.metadata.namespace
            })

    except Exception as e:
        # Handle any exceptions
        return JsonResponse({"error": str(e)})

    return render(request, 'list_workloads.html', context={'list_workloads': list_workloads})



def list_replica_sets(request):
    try:
       # Load the kubeconfig file (usually located at ~/.kube/config)
       config.load_kube_config()

       # Create an instance of the AppsV1Api class
       apps_v1 = client.AppsV1Api()

       # Get the list of deployments in all namespaces
     
       replica_sets = apps_v1.list_replica_set_for_all_namespaces(watch=False)
     
        
       # Extract and print the names and namespaces of the deployments
       replica_set_list = []
       for rs in replica_sets.items:
        rs_info = {
            "name": rs.metadata.name,
            "namespace": rs.metadata.namespace
        }
        replica_set_list.append(rs_info)

       return render(request, 'replica_sets_list.html', context={'replica_sets_list': replica_set_list})
    except Exception as e:
        # Handle any exceptions
        return JsonResponse({"error": str(e)})



def list_deployments(request):
    try:
       # Load the kubeconfig file (usually located at ~/.kube/config)
       config.load_kube_config()

       # Create an instance of the AppsV1Api class
       apps_v1 = client.AppsV1Api()

       # Get the list of deployments in all namespaces
     
       deployments = apps_v1.list_deployment_for_all_namespaces(watch=False)
     
        
       # Extract and print the names and namespaces of the deployments
       deployment_list = []
       for deployment in deployments.items:
           deployment_info = {
               "name": deployment.metadata.name,
               "namespace": deployment.metadata.namespace
           }
           deployment_list.append(deployment_info)

       return render(request, 'deployments_list.html', context={'deployments_list': deployment_list})
    except Exception as e:
        # Handle any exceptions
        return JsonResponse({"error": str(e)})

def list_pods(request):
    try:
        # Load Kubernetes configuration from default kubeconfig file
        config.load_kube_config()

        # Create Kubernetes API client
        api_instance = client.CoreV1Api()

        # Retrieve list of pods
        pods = api_instance.list_pod_for_all_namespaces(watch=False)

        # Extract relevant information from pods
        pod_list = []
        for pod in pods.items:
            pod_info = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "ip": pod.status.pod_ip,
            }
            pod_list.append(pod_info)

        #return JsonResponse({"pods": pod_list})
        return render(request, 'pods_list.html', context={'pod_list': pod_list})

    except Exception as e:
        # Handle any exceptions
        return JsonResponse({"error": str(e)})

def create_pods(request):
    form = CreatePodForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                # Load Kubernetes configuration from default kubeconfig file
                config.load_kube_config()

                # Create Kubernetes API client
                api_instance = client.CoreV1Api()

                # Extract form data
                pod_name = form.cleaned_data['name']
                image = form.cleaned_data['image']
                namespace = form.cleaned_data.get('namespace', 'default')

                # Check if namespace exists, if not, create it
                try:
                    api_instance.read_namespace(namespace)
                except ApiException as e:
                    if e.status == 404:
                        # Namespace doesn't exist, create it
                        new_namespace = client.V1Namespace(metadata=client.V1ObjectMeta(name=namespace))
                        api_instance.create_namespace(body=new_namespace)
                    else:
                        raise  # Propagate other exceptions

                # Define pod spec
                pod_manifest = {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": pod_name, "namespace": namespace},
                    "spec": {
                        "containers": [{
                            "name": pod_name,
                            "image": image,
                            # Add more pod spec details as needed
                        }]
                    }
                }

                # Create the pod
                api_instance.create_namespaced_pod(namespace=namespace, body=pod_manifest)

                #return HttpResponse("Pod created successfully!")
                return redirect(reverse('list_pods'))
            except ApiException as e:
                return HttpResponse(f"Error creating pod: {e}")
    
    return render(request, 'create_pods.html', {'form': form})

def edit_pod(request, namespace, name):

    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()

        apps_v1 = client.CoreV1Api()
        pod = apps_v1.read_namespaced_pod(name=name, namespace=namespace)
        pod_yaml = yaml.dump(pod.to_dict())
        if request.method == 'POST':
            edited_yaml = request.POST['pod_yaml']
            edited_pod = yaml.safe_load(edited_yaml)
            # Create a patch object with only editable fields
            patch = {
                "spec": {
                    "containers": [
                        {
                            "name": pod.spec.containers[0].name,
                            "image": edited_pod['spec']['containers'][0].get('image', pod.spec.containers[0].image),
                            "env": edited_pod['spec']['containers'][0].get('env', pod.spec.containers[0].env),
                            "resources": edited_pod['spec']['containers'][0].get('resources', pod.spec.containers[0].resources),
                        }
                    ]
                }
            }
            apps_v1.patch_namespaced_pod(name=name, namespace=namespace, body=patch)
            #apps_v1.replace_namespaced_pod(name=name, namespace=namespace, body=edited_pod)
            return redirect(reverse('list_pods'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'edit_pod.html', {'pod_yaml': pod_yaml, 'namespace': namespace, 'name': name})

# def edit_replica_set(request, namespace, name):
#     try:
#         # Load the kubeconfig file (usually located at ~/.kube/config)
#         config.load_kube_config()

#         apps_v1 = client.AppsV1Api()
#         replica_set = apps_v1.read_namespaced_replica_set(name=name, namespace=namespace)
#         replica_set_yaml = yaml.dump(replica_set)
#         # replica_set_dict = {
#         #     "apiVersion": replica_set.api_version,
#         #     "kind": replica_set.kind,
#         #     "metadata": {
#         #         "annotations": replica_set.metadata.annotations,
#         #         "creationTimestamp": replica_set.metadata.creation_timestamp,
#         #         "deletionGracePeriodSeconds": replica_set.metadata.deletion_grace_period_seconds,
#         #         "deletionTimestamp": replica_set.metadata.deletion_timestamp,
#         #         "finalizers": replica_set.metadata.finalizers,
#         #         "generateName": replica_set.metadata.generate_name,
#         #         "generation": replica_set.metadata.generation,
#         #         "labels": replica_set.metadata.labels,
#         #         "name": replica_set.metadata.name,
#         #         "namespace": replica_set.metadata.namespace,
#         #         "resourceVersion": replica_set.metadata.resource_version,
#         #         "uid": replica_set.metadata.uid,
#         #     },
#         #     "spec": {
#         #         "replicas": replica_set.spec.replicas,
#         #         "selector": replica_set.spec.selector.match_labels,
#         #         "template": {
#         #             "metadata": replica_set.spec.template.metadata.labels,
#         #             "spec": replica_set.spec.template.spec.containers,
#         #         }
#         #     },
#         # }

#         # # Convert the dictionary to YAML
#         # replica_set_yaml = yaml.dump(replica_set_dict)

#         if request.method == 'POST':
#             edited_yaml = request.POST['replica_set_yaml']
#             edited_replica_set = yaml.safe_load(edited_yaml)
#             # Create a patch object with only editable fields
#             patch = {
#                 "spec": {
#                     "replicas": edited_replica_set['spec'].get('replicas', replica_set.spec.replicas),
#                     "template": {
#                         "spec": {
#                             "containers": [
#                                 {
#                                     "name": replica_set.spec.template.spec.containers[0].name,
#                                     "image": edited_replica_set['spec']['template']['spec']['containers'][0].get('image', replica_set.spec.template.spec.containers[0].image),
#                                     "env": edited_replica_set['spec']['template']['spec']['containers'][0].get('env', replica_set.spec.template.spec.containers[0].env),
#                                     "resources": edited_replica_set['spec']['template']['spec']['containers'][0].get('resources', replica_set.spec.template.spec.containers[0].resources),
#                                 }
#                             ]
#                         }
#                     }
#                 }
#             }
#             apps_v1.patch_namespaced_replica_set(name=name, namespace=namespace, body=patch)
#             return redirect(reverse('list_replica_sets'))
#     except Exception as e:
#             # Handle any exceptions
#             return JsonResponse({"error": str(e)})
#     return render(request, 'edit_replica_set.html', {'replica_set_yaml': replica_set_yaml, 'namespace': namespace, 'name': name})

def edit_replica_set(request, namespace, name):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()

        apps_v1 = client.AppsV1Api()
        replica_set = apps_v1.read_namespaced_replica_set(name=name, namespace=namespace)
        replica_set_yaml = yaml.dump(replica_set.to_dict())
        if request.method == 'POST':
            edited_yaml = request.POST['replica_set_yaml']
            edited_replica_set = yaml.safe_load(edited_yaml)
            # Create a patch object with only editable fields
            patch = {
                "spec": {
                    "replicas": edited_replica_set['spec'].get('replicas', replica_set.spec.replicas),
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": replica_set.spec.template.spec.containers[0].name,
                                    "image": edited_replica_set['spec']['template']['spec']['containers'][0].get('image', replica_set.spec.template.spec.containers[0].image),
                                    "env": edited_replica_set['spec']['template']['spec']['containers'][0].get('env', replica_set.spec.template.spec.containers[0].env),
                                    "resources": edited_replica_set['spec']['template']['spec']['containers'][0].get('resources', replica_set.spec.template.spec.containers[0].resources),
                                }
                            ]
                        }
                    }
                }
            }
            apps_v1.patch_namespaced_replica_set(name=name, namespace=namespace, body=patch)
            return redirect(reverse('list_replica_sets'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'edit_replica_set.html', {'replica_set_yaml': replica_set_yaml, 'namespace': namespace, 'name': name})


def edit_deployment(request, namespace, name):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()

        apps_v1 = client.AppsV1Api()
        deployment = apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
        deployment_yaml = yaml.dump(deployment.to_dict())
        if request.method == 'POST':
            edited_yaml = request.POST['deployment_yaml']
            edited_deployment = yaml.safe_load(edited_yaml)
            # Create a patch object with only editable fields
            patch = {
                "spec": {
                    "replicas": edited_deployment['spec'].get('replicas', deployment.spec.replicas),
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": deployment.spec.template.spec.containers[0].name,
                                    "image": edited_deployment['spec']['template']['spec']['containers'][0].get('image', deployment.spec.template.spec.containers[0].image),
                                    "env": edited_deployment['spec']['template']['spec']['containers'][0].get('env', deployment.spec.template.spec.containers[0].env),
                                    "resources": edited_deployment['spec']['template']['spec']['containers'][0].get('resources', deployment.spec.template.spec.containers[0].resources),
                                }
                            ]
                        }
                    }
                }
            }
            apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=patch)
            return redirect(reverse('list_deployments'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'edit_deployment.html', {'deployment_yaml': deployment_yaml, 'namespace': namespace, 'name': name})

def apply_yaml(yaml_text):
    """Apply YAML configuration to the Kubernetes cluster."""
    
    config.load_kube_config()
    
    k8s_client = client.ApiClient()
    
    try:
        # Load and parse the YAML text
        k8s_objects = yaml.safe_load_all(yaml_text)
        
        for obj in k8s_objects:
            utils.create_from_dict(k8s_client, obj)
            
        print("YAML successfully applied.")
        
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
    except ApiException as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def apply_yaml_view(request):
    try:
        if request.method == 'POST':
            yaml_text = request.POST['yaml_text']
            apply_yaml(yaml_text)
            return redirect(reverse('list_workloads'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'apply_yaml.html')


def delete_pod(request, namespace, name):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()
        apps_v1 = client.CoreV1Api()

        if request.method == 'POST':
            apps_v1.delete_namespaced_pod(name=name, namespace=namespace)
            return redirect(reverse('list_pods'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'confirm_delete.html', {'namespace': namespace, 'name': name})

def delete_replica_set(request, namespace, name):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()

        if request.method == 'POST':
            apps_v1.delete_namespaced_replica_set(name=name, namespace=namespace)
            return redirect(reverse('list_replica_sets'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'confirm_delete_replica_set.html', {'namespace': namespace, 'name': name})


def delete_deployment(request, namespace, name):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()
        apps_v1 = client.AppsV1Api()

        if request.method == 'POST':
            apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
            return redirect(reverse('list_deployments'))
    except Exception as e:
            # Handle any exceptions
            return JsonResponse({"error": str(e)})
    return render(request, 'confirm_delete_deployment.html', {'namespace': namespace, 'name': name})

def list_namespaces(request):
    try:
        # Load the kubeconfig file (usually located at ~/.kube/config)
        config.load_kube_config()

        # Create an instance of the API class
        v1 = client.CoreV1Api()

        # Get the list of namespaces
        namespaces = v1.list_namespace()
        namespaces_list = [ns.metadata.name for ns in namespaces.items]

        return render(request, 'namespaces_list.html', context={'namespaces_list': namespaces_list})
    except Exception as e:
        # Handle any exceptions
        return JsonResponse({"error": str(e)})




def create_namespaces(request):
    form = CreateNamespaceForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                # Load Kubernetes configuration from default kubeconfig file
                config.load_kube_config()

                # Create Kubernetes API client
                api_instance = client.CoreV1Api()

                # Extract form data
                namespace_name = form.cleaned_data['name']


                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": namespace_name},
                }
                api_instance.create_namespace(namespace_manifest)


                #return HttpResponse("Pod created successfully!")
                return redirect(reverse('list_namespaces'))
            except ApiException as e:

                if e.status == 409:
                
                    return HttpResponse(f"Namespace '{namespace_name}' already exists. {e}")
    
                else:
                    return HttpResponse(f"Failed to create namespace '{namespace_name}': {e}")


             
    return render(request, 'create_namespaces.html', {'form': form})