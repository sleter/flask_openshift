import os, logging, socket, yaml, kubernetes
from flask import Flask, jsonify, render_template
from kubernetes import client, config
from openshift.dynamic import DynamicClient

HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS', 'localhost')
APP_NAME = os.environ.get('OPENSHIFT_APP_NAME', 'flask')
IP = os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
HOME_DIR = os.environ.get('OPENSHIFT_HOMEDIR', os.getcwd())
NAMESPACE = os.environ.get('OPENSHIFT_NAMESPACE', 'default')

log = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_pod')
def add_pod():

    #c = config.load_incluster_config()
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    #oapi = client.OapiApi(oclient_config)
    #kclient_config = config.load_kube_config()
    #api = kubernetes.client.CoreV1Api(kclient_config)
    
    v1_pod = dyn_client.resources.get(api_version='v1', kind='Pod')

    pod = """
    kind: Pod
    metadata:
      name: alpine
      namespace: nvidia
    spec:
      containers:
      - image: alpine:latest
        command:
          - /bin/sh
          - "-c"
          - "sleep 60m"
        imagePullPolicy: IfNotPresent
        name: alpine
    """

    pod_data = yaml.load(pod)
    #resp = api.create_namespaced_pod(body=pod_data, namespace='flask-app')
    #resp = oapi.create_namespaced_pod(body=pod_data, namespace='flask-app')
    resp = v1_pod.create(body=pod_data, namespace='flask-app')

    # resp is a ResourceInstance object
    return jsonify({'data': resp.metadata.self_link})
    

@app.route('/info')
def info():
    return jsonify({
        'host_name': HOST_NAME,
        'app_name': APP_NAME,
        'ip': IP,
        'port': PORT,
        'home_dir': HOME_DIR,
        'host': socket.gethostname(),
        'namespace': NAMESPACE
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
