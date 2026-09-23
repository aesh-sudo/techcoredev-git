pipeline {
    agent {
        docker {
            image 'lachlanevenson/k8s-kubectl:v1.25.0'
            args '--entrypoint= --network=minikube'
        }
    }
    stages {
        stage('Deploy to K8s') {
            steps {
                withCredentials([file(credentialsId: 'minikube-config', variable: 'KUBECONFIG')]) {
                    sh '''
                        curl -fsSL -o helm.tar.gz https://get.helm.sh/helm-v3.14.3-linux-amd64.tar.gz
                        tar -xzf helm.tar.gz
                        export PATH=$PWD/linux-amd64:$PATH
                        helm upgrade --install my-app ./helm-charts/my-app-chart --set image.tag=${BUILD_NUMBER}
                    '''
                    sh 'kubectl get pods'
                }
            }
        }
    }
}
