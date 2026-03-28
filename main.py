'''
Main execution entry point for the compliance QA pipeline
'''

import uuid
import json
import logging
from pprint import pprint

from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.graph.workflow import app

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("brand-guardian-runner")

def run_cli_simulation():
    '''
    Simulates the video compliance audit request
    '''

    # genrates the session ID
    session_id = str(uuid.uuid4())
    logging.info(f"Starting audit session: {session_id}")

    #define the initial state
    initial_inputs = {
        "video_url" : "",
        "video_id" :f"vid_{session_id[:8]}",
        "compliance_results" :[],
        "errors":[]
    }

    print("/n---------------Initializing the workflow------------------")
    print(f"Input payload : {json.dumps(initial_inputs,indent=2)}")

    try:
        final_state = app.invoke(initial_inputs)
        print("/n--------------Workflow execution is complete----------------")

        print("/nCompliance Audit report == ")
        print(f"/n Video ID : {final_state.get('video_id')}")
        print(f"Status : {final_state.get('final_status')}")
        print("/n [VIOLATIONS DETECTED]")
        results = final_state.get('comliance_results',[])
        if results:
            for issue in results:
                print(f"-[{issue.get('severity')}] [{issue.get('category')}] [{issue.get('description')}]")
        else:
            print("No violations are detected......")
        print("/n[FINAL SUMMARY]")
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow Execution Failed : {str(e)}")
        raise e
    
if __name__ == "main" :
    run_cli_simulation()
