import json 
import os
import logging
import re
from typing import Dict,Any,List

from langchain_openai import AzureChatOpenAI , AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import AzureSearch
from langchain_core.messages import SystemMessage,HumanMessage
from sqlalchemy import text


# Import state from schema
from backend.src.graph.state import VideoAuditState,ComplianceIssue

# Import service
from backend.src.services.video_indexer import VideoIndexerService

# configure the logger

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

# Node 1 : Indexer
# Funtion to convert video to text

def index_video_node(state:VideoAuditState)->Dict[str,Any]:
    '''
    Downloads the youtube video from the url
    Uploads to the Azure Video Indexer
    extracts the insights 
    '''

    video_url = state.get('video_url')
    video_id_input = state.get('video_id','vid_demo')

    logger.info(f"-----[Node:Indexer] Processing: {video_url}")

    local_filename = "temp_audio_video.mp4"

    try:
        vi_service = VideoIndexerService()
        # Download the video (yt-dlp)
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url,output_path=local_filename)
        else:
            raise Exception("Please provde a valid Youtube URL for this test")
        # Upload to Azure Video Indexer
        azure_video_id = vi_service.upload_video(local_path,video_name=video_id_input)
        logger.info(f"Upload Success. Azure Video ID: {azure_video_id}")

        # cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

        # wait
        raw_insights = vi_service.wait_for_processing(azure_video_id)

        #extract
        clean_data = vi_service.extract_data(raw_insights)
        logger.info(
            "[NODE:Indexer] VI extracted: transcript_len=%s ocr_lines=%s metadata=%s",
            len(clean_data.get("transcript") or ""),
            len(clean_data.get("ocr_text") or []),
            clean_data.get("video_metadata"),
        )
        logger.info("----[NODE:Indexer] Extraction Completed---------")
        return clean_data

    except Exception as e:
        logger.error(f"Video Indexer Failed:{e}")
        return {
            "errors":[str(e)],
            "final_status":"FAIL",
            "transcript":"",
            "ocr_text":[],
        }

# Node 2 : Compliance Auditor
def audit_content_node(state:VideoAuditState)->Dict[str,Any]:
    '''
    Performs Retrieval augmented genration to audit the content - brand video
    '''

    logger.info("-----[NODE: Auditor] Quering the knowledge base and LLM")
    transcript = state.get('transcript','')

    if not transcript:
        logger.warning("No transcript available. Skipping audit......")
        return {
            "final_status":"FAIL",
            "final_report":"Audit skipped because no transcript was found"
        }

    # Initialize clients (endpoint + api_key explicit — same as backend/scripts/index_documents.py)
    _api_version = (os.getenv("AZURE_OPENAI_API_VERSION") or "").strip().strip('"') or "2024-12-01-preview"
    _endpoint = (os.getenv("AZURE_OPENAI_ENDPOINT") or "").strip().strip('"')
    _embedding_dep = (os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or "").strip().strip('"')
    logger.info(
        "[NODE:Auditor] Azure OpenAI: endpoint host=%s embedding_deployment=%s api_version=%s",
        _endpoint.replace("https://", "").split("/")[0] if _endpoint else "(missing)",
        _embedding_dep or "(missing)",
        _api_version,
    )

    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        azure_endpoint=_endpoint,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=_api_version,
        temperature=0.0,
    )

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=_embedding_dep,
        azure_endpoint=_endpoint,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=_api_version,
    )
    
    vector_store = AzureSearch(
        azure_search_endpoint= os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key = os.getenv("AZURE_SEARCH_KEY"),
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function= embeddings.embed_query
    )

    # RAG Retrival
    ocr_text = state.get("ocr_text",[])
    query_text = f"{transcript} {''.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text , k=3)
    retrieved_rules = "/n/n".join([doc.page_content for doc in docs])

    system_prompt = f"""
    You are a senior brand compliance auditor.
    OFFICIAL REGULATORY RULES:
    {retrieved_rules}
    INSTRUCTIONS:
    1.Analyze the transcript and OCR text below.
    2.Identify any violations of the rules.
    3.Return strictly JSON in the following format:
    {{
    "compliance_results":[
    {{
        "category":"Claim Validation",
        "severity : "CRITICAL",
        "description":"Explanation of the violation..."
    }}
    ],
    "status":"FAIL",
    "final_report":"Summary of findings..."
    }}

    If no violations are found, set "status" to "PASS" and "compliance_results" to []
    """

    user_message = f"""
    VIDEO_METADATA :{state.get('video_metadata',{})}
    TRANSCRIPT = {transcript}
    ON_SCREEN TEXT (OCR) = {ocr_text}
    """

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        content = response.content
        if "```" in content:
            content = re.search(r"```(?:json)?(.?)```",content,re.DOTALL).group(1)
        
        audit_data = json.loads(content.strip())
        return{
            "compliance_results" :audit_data.get("compliance_results",[]),
            "final_status" : audit_data.get("status","FAIL"),
            "final_report" : audit_data.get("final_report","No report generated")
        }

    except Exception as e:
        logger.error(f"System Error in auditor Node:{str(e)}")

        #loggin the raw response
        logger.error(f"Raw LLM Response : {response.content if 'response' in locals() else 'None'}")

        return{
            "errors": [str(e)],
            "final_status":"FAIL"
        }