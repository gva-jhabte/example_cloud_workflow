from flask import Flask, request, jsonify, make_response
import gva.logging
from gva.services import create_http_task
import uuid
import os
from flask_sslify import SSLify
from flask_cors import CORS

from gva.logging import get_logger
logger = get_logger()
logger.setLevel(5)

app = Flask(__name__)
CORS(app, supports_credentials=True)
sslify = SSLify(app)

@app.route('/<job_name>/<action>', methods=['POST'])
def process_command(job_name, action):
    print('running process_command')
    if action.lower() != 'start':
        return "invalid action", 500
    try:
        job_name = job_name.lower()
        context = request.form.to_dict() # we may get passed other info in the request
        context['job_name'] = job_name
        context['uuid'] = str(uuid.uuid4())
        context['task-flow'] = 'start'  # all flows begin with a 'start'
        # TODO: create an entry in the database for this job
        os.system('./microservice.sh')
        with open("output.yaml") as f:
            for line in f:
                name = ''.join(line.split())
                create_http_task(project='jon-deploy-project',
                                queue='my-queue',
                                url=F"https://{name}.jon-deploy.com/{job_name}",
                                payload=context)
        message = F"[API_GATEWAY_SCHEDULER] Job {job_name} triggered with identifier {context.get('uuid')}"
        logger.debug(message)
        return message
    except Exception as err:
        message = F"[API_GATEWAY_SCHEDULER] Job {job_name} trigger failed - {type(err).__name__} - {err}"
        logger.error(message)
        return message, 500

if __name__ == "__main__":
    app.run(ssl_context="adhoc", host="0.0.0.0", port=8080)
