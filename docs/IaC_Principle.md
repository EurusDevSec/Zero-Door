# IaC for yaml config

> k3d config:

## \* Create Cluster by yaml File:

```
k3d cluster --create config <path>(infrastructure/k3d-config.yaml)
```

## \* List all cluster

k3d cluster list

```
`ACER@LAPTOP-78LVMDCQ MINGW64` /r/_Projects/Eurus_Workspace zero_door (infra/k8s-cluster-setup)

$ k3d cluster list

NAME        SERVERS   AGENTS   LOADBALANCER
zero-door   1/1       2/2      true
```

## \* Delete cluster

```
k3d cluster delete <name-cluster>(zero-door)
```
