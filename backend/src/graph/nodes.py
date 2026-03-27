import json 
import os
import logging
import re
from typing import Dict,Any,List

from langchain_openai import AzureChatOpenAI , AzureOpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import AzureSearch
from langchain_core.messages import SystemMessage,HumanMessage


# Import state from schema
from backend.src.graph.state import VideoAuditState,ComplianceIssue

# Import service
from backend.src.services.video_indexer import VideoIndexerService

# configure the logger

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

# Node 1 : INdexer

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
        # Download the video
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url,output_path=local_filename)
        else:
            raise Exception("Please provde a valid Youtube URL for this test")
        # Upload to Azure Video Indexer
        azure_video_id = vi_service.upload_video(local_path,video_name= video_id_input)
        logger.info(f"Upload Success. Azure Video ID: {azure_video_id}")

        # cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

        # wait
        raw_insights = vi_service.wait_for_processing(azure_video_id)

        #extract
        clean_data = vi_service.extract_data(raw_insights)
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