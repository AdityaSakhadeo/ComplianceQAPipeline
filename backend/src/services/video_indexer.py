'''
Connector :  Python and Azure Video Indexer
'''
import os
import time
import logging
import requests
import yt_dlp
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("video-indexer")

class VideoIndexerService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_VI_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_VI_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME","brand-compliance-project")
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        '''
        Genrates an ARM Access token
        '''     

        try:
            token_object = self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"Failed to get the Azure token : {e}")
            raise

    def get_account_token(self,arm_access_token):
        '''
        Exchanges the ARM token for Video indexer account team
        '''
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )
        headers = {"Authorization" : f"Bearer {arm_access_token}"}
        payload = {"permissionType" : "Contributor", "scope":"Account"}
        response = requests.post(url,headers=headers,json=payload)

        if response.status_code != 200:
            raise Exception(f"Failed to get VI account token : {response.text}")
        return response.json().get("accessToken")
    
    # Funtion to download the youtube video
    def download_youtube_video(self,url,output_path="temp_video.mp4"):
        '''
        Downloads the youtube video in the local file
        '''
        logger.info(f"Downloading youtube video : {url}")

        ydl_opts = {
            'format' : 'best',
            'outtmpl' : output_path,
            'quiet' : False,
            'no_warning' : False,
            'extractor_args':{'youtube':{'player_client':['android','web']}},
            'http_headers':{
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36"
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info(f"Download complete")
            return output_path
        except Exception as e:
            raise Exception(f"Youtube video download failed : {e}")
        
    # Funtion to upload the video to video indexer
    def upload_video(self,video_path,video_name):
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)

        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"

        parms = {
            "accessToken":vi_token,
            "name" : video_name,
            "privacy":"Private",
            "indexingPreset":"Default"
        }

        logger.info(f"Uploading the file {video_path} to Azure ....")

        # open the file in binary and stream it on azure

        with open(video_path,'rb') as video_file:
            files = {'file':video_file}
            response = requests.post(api_url,params=parms,files=files)

        if response.status_code != 200 :
            raise Exception(f"Azure upload Failed : {response.text}")
        
        video_id = response.json().get("id")
        logger.info(f"Video uploaded successfully with ID: {video_id}")
        return video_id
        
    
    def wait_for_processing(self, video_id):
        """Polls status until complete."""
        logger.info(f"Waiting for video {video_id} to process...")
        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)
            
            url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index"
            params = {"accessToken": vi_token}
            response = requests.get(url, params=params)
            data = response.json()
            
            state = data.get("state")
            if state == "Processed":
                logger.info(
                    "Video Indexer index payload: top-level keys=%s videos=%s",
                    list(data.keys()),
                    len(data.get("videos") or []),
                )
                return data
            elif state == "Failed":
                raise Exception("Video Indexing Failed in Azure.")
            elif state == "Quarantined":
                raise Exception("Video Quarantined (Copyright/Content Policy Violation).")
            
            logger.info(f"Status: {state}... waiting 30s")
            time.sleep(30)



    def extract_data(self,vi_json):
        'parses the JSON into our state format'
        transcript_lines = []
        for v in vi_json.get("videos",[]):
            for insight in v.get("insights",{}).get("transcript",[]):
                if insight.get("text"):
                    transcript_lines.append(insight.get("text"))

        ocr_lines =[]
        for v in vi_json.get("videos",[]):
            for insight in v.get("insights",{}).get("ocr",[]):
                if insight.get("text"):
                    ocr_lines.append(insight.get("text"))

        out = {
            "transcript":" ".join(transcript_lines),
            "ocr_text" : ocr_lines,
            "video_metadata" : {
                "duration" : vi_json.get("summarizedInsights",{}).get("duration"),
                "platform" : "youtube"
            }

        }
        preview = (out["transcript"] or "")[:400]
        logger.info(
            "extract_data: transcript_segments=%s ocr_segments=%s transcript_preview=%r",
            len(transcript_lines),
            len(ocr_lines),
            preview + ("..." if len(out["transcript"] or "") > 400 else ""),
        )
        return out           