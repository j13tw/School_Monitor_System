#! /usr/bin/python3 

import os, sys, ssl
from kubernetes import client, config
from flask import render_template

'''
[Kubernetes Base Setup]
Cluster Help Command = "kubeadm token create --print-join-command" 
'''
kubernetesToken = ""
kubernetesConfigure = client.Configuration()
kubernetesConfigure.host = "https://10.0.0.224:6443"
kubernetesConfigure.verify_ssl=False
kubernetesConfigure.api_key = {"authorization": "Bearer " + kubernetesToken}
kubernetesApiClient = client.ApiClient(kubernetesConfigure)

'''
[Get Pod With All NameSpace]
'''
kubernetesApiV1 = client.CoreV1Api(kubernetesApiClient)
print("Listing pods with their IPs:")
ret = kubernetesApiV1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" %(i.status.pod_ip, i.metadata.namespace, i.metadata.name))
