import sys
from kubernetes import client, config

def list_deployments(namespace):
    # Configura o acesso ao cluster Kubernetes
    config.load_kube_config()  # Certifique-se de que seu KUBECONFIG está configurado corretamente

    # Cria uma instância da API de Apps (v1) do Kubernetes
    api_instance = client.AppsV1Api()

    # Obtém a lista de deployments no namespace especificado
    deployments = api_instance.list_namespaced_deployment(namespace)

    # Coleta e imprime os nomes dos deployments, o número de réplicas atuais, e os containers
    deployment_info = []
    for deployment in deployments.items:
        if deployment.status.replicas is not None:
            containers = []
            for container in deployment.spec.template.spec.containers:
                resources = container.resources
                requests = resources.requests if resources.requests else {}
                limits = resources.limits if resources.limits else {}
                
                container_info = {
                    'name': container.name,
                    'image': container.image,
                    'requests': {
                        'cpu': requests.get('cpu', 'não configurado'),
                        'memory': requests.get('memory', 'não configurado')
                    },
                    'limits': {
                        'cpu': limits.get('cpu', 'não configurado'),
                        'memory': limits.get('memory', 'não configurado')
                    }
                }
                containers.append(container_info)
            
            deployment_info.append({
                'name': deployment.metadata.name,
                'replicas': deployment.status.replicas,
                'containers': containers
            })

    # Imprime as informações coletadas
    for info in deployment_info:
        print(f"Deployment: {info['name']}, Réplicas Atuais: {info['replicas']}")
        for container in info['containers']:
            print(f"  Container: {container['name']}, Imagem: {container['image']}")
            print(f"    Requests: CPU: {container['requests']['cpu']}, Memória: {container['requests']['memory']}")
            print(f"    Limits: CPU: {container['limits']['cpu']}, Memória: {container['limits']['memory']}")

    return deployment_info

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <namespace>")
        sys.exit(1)

    namespace = sys.argv[1]

    # Abre um arquivo para redirecionar a saída
    with open("output.txt", "w") as f:
        # Redireciona sys.stdout para o arquivo
        original_stdout = sys.stdout
        sys.stdout = f

        try:
            # Executa a função e imprime as saídas
            deployment_info = list_deployments(namespace)
        finally:
            # Restaura sys.stdout para seu valor original
            sys.stdout = original_stdout
