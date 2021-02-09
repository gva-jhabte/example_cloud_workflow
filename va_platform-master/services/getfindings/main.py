from gva.services import GoogleTaskOperator
from flask import Flask, request, jsonify, make_response
from operators import FakeGetFindingssOperator, SaveStringToBlobOperator
from gva.flows.operators import EndOperator
from gva.flows import runner
import gva.logging

CREDENTIALS_FILE = "jon-deploy-project-150f60b0b3c3.json"

app = Flask(__name__)

get_hosts = FakeGetFindingssOperator()
save_string = SaveStringToBlobOperator(project='jon-deploy-project', bucket='jonhab-test', path="%Y%m%d%_%h%M%S-%f.string", credentials_file=CREDENTIALS_FILE)
create_gcp_cloud_task = GoogleTaskOperator(credentials_file=CREDENTIALS_FILE)
end = EndOperator()

flow = get_hosts > save_string > create_gcp_cloud_task > end

logger = gva.logging.get_logger()
logger.setLevel(10)

@app.route('/', methods=['POST'])
def process_command():
    try:
        context = request.get_json(force=True)
        job_name = context.get('job_name')

        runner.go(flow=flow, context=context)

        message = F"[GETFINDINGS] {job_name} run okay - {context.get('uuid')}"
        logger.debug(message)
        return message
    except Exception as err:
        message = F"[GETFINDINGS] {job_name} failed - {context.get('uuid')} - {type(err).__name__} - {err}"
        logger.error(message)
        return message, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2100)
 
