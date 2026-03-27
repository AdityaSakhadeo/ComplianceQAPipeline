import operator
from typing import Annotated,List,Dict,Optional,Any,TypedDict

# Define the schema for a single compliance result
class ComplianceIssue(TypedDict):
    category: str # e.g., "Inappropriate Content", "Copyright Violation"
    severity: str  # CRITICAL | WARNING
    description: str # Detailed description of the issue
    timestamp: Optional[str]  # ISO format timestamp

# Define the global graph state
class VideoAuditState(TypedDict):
    '''
    Defines the data schema for langgraph execution content
    Main container that holds everything, all the video information and the reports and results as well for the particular video
    '''
    # Input parameters
    video_url : str
    video_id : str

    # Ingestion and extraction data
    local_file_path: Optional[str]
    video_metadata : Dict[str, Any] # e.g. [{"duration": "5 mins", "resolution": "1080p"}]
    transcript : Optional[str]  # fully extracted speech-to-text transcript
    ocr_text : List[str]

    # Analysis output
    compliance_results : Annotated[List[ComplianceIssue],operator.add ]

    # Final Deliverables:
    final_status :str
    final_report : str

    # System Observability
    # errors : API timeouts , system level errors
    errors : Annotated[List[str],operator.add]