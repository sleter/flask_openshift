import os, logging, socket, yaml
from flask import Flask, jsonify, render_template
from kubernetes import client, config
from openshift.dynamic import DynamicClient

HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS', 'localhost')
APP_NAME = os.environ.get('OPENSHIFT_APP_NAME', 'flask')
IP = os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
HOME_DIR = os.environ.get('OPENSHIFT_HOMEDIR', os.getcwd())

log = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_pod')
def add_pod():
    
    config.load_incluster_config()
    #k8s_client = config.new_client_from_config()
    k8s_client = client.CoreV1Api()
    dyn_client = DynamicClient(k8s_client)

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
      restartPolicy: Always
    """

    pod_data = yaml.load(pod)
    resp = v1_pod.create(body=pod_data, namespace='nvidia')

    return resp.metadata
    

@app.route('/info')
def info():
    return jsonify({
        'host_name': HOST_NAME,
        'app_name': APP_NAME,
        'ip': IP,
        'port': PORT,
        'home_dir': HOME_DIR,
        'host': socket.gethostname()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
