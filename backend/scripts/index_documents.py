import os 
import glob
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

#Document loaders and splitters

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import azure compoenents
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

# set up logging and config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("indexer")

def index_docs():
    '''
    Reads the PDFs , chunks them, and upload them to Azure AI Search
    '''

    # Define paths, we look for data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir,"../../backend/data")

    # Check on the environement variables
    logger.info("="*60)
    logger.info("Environment variable check")
    logger.info(f"AZURE_OPENAI_ENDPOINT:{os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION:{os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT:{os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT:{os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME:{os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("="*60)

    #Validate the required environment variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environement variables:{missing_vars}")
        logger.error("Please check your env file and ensure that all the variables are set")

    # Initialize the embedding model - Turns your text into vectors
    try:
        logger.info("Initializing azure openai embeddings......")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT','text-embedding-3-small'),
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION","2024-12-01-preview")
        )
        logger.info("Embedding model initialized succesfully")

    except Exception as e:
        logger.error(f"Failed to initialize the embeddings : {e}")
        logger.error("Please verify your Azure OpenAI deployment name and endpoint")
        return
    
    # Initialize the Azure Search

    try:
        logger.info("Initializing Azure AI Search vector store......")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv('AZURE_SEARCH_ENDPOINT'),
            azure_search_key = os.getenv("AZURE_SEARCH_KEY"),
            index_name = index_name,
            embedding_function = embeddings.embed_query
        )
        logger.info("Vector store initialized for index : {index_name}")

    except Exception as e:
        logger.error(f"Failed to initialize the azure search : {e}")
        logger.error("Please verify your Azure Search endpoint,API key and index name")
        return
    
    # Find PDF files
    pdf_files = glob.glob(os.path.join(data_folder,"*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder} Please add the files")
    logger.info(f"Found {len(pdf_files)} PDFs to process : {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    # process each pdf 
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading:{os.path.basename(pdf_path)}.........")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            # Chunking strategy
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )

            splits = text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)

            all_splits.extend(splits)
            logger.info(f"Split info {len(splits)} chunks.")

        except Exception as e :
            logger.error(f"Falied to process {pdf_path} : {e}")

        # Upload to azure
        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Index '{index_name}' ")
            try:
                # azure search accepts batches automatically via this method
                vector_store.add_documents(documents = all_splits)
                logger.info("="*60)
                logger.info("Indexing Complete!! Knowledge base is ready...")
                logger.info(f"Total chunks indexed :{len(all_splits)}")
                logger.info("="*60)
            except Exception as e:
                logger.error(f"Failed to upload the documents to azure search : {e}")
                logger.error("Please check the azure search configuration and try again")
        
        else:
            logger.warning("No documents werer processed")
        
if __name__== "__main__":
    index_docs()

