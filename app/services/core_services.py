from elasticsearch import Elasticsearch
import json
import os
import time
from app.config import ELASTICSEARCH_URI, MAPPINGS_PATH
from sentence_transformers import SentenceTransformer
import logging

# Initialize Elasticsearch client
es_client = Elasticsearch(ELASTICSEARCH_URI)
embeddings_model = None

logger = logging.getLogger(__name__)


def load_mappings():
    try:
        with open(MAPPINGS_PATH, "r") as f:
            mappings = json.load(f)
        return mappings
    except Exception as e:
        logger.error(f"Failed to load mappings file: {str(e)}")
        exit(1)


def seed_database_with_sample_data():
    try:
        # Delete all documents in the 'pokemon' index
        es_client.delete_by_query(index="pokemon", body={"query": {"match_all": {}}})

        # Get the directory path of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Navigate to the pokemon/ directory (at the same level as app/)
        pokemon_dir = os.path.join(current_dir, "../../", "pokemon")

        # Iterate through all JSON files in the pokemon/ directory
        for filename in os.listdir(pokemon_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(pokemon_dir, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    try:
                        document = json.load(file)
                        # Combine fields for embedding generation
                        text = f"{document.get('description', '')} {document.get('name', '')} {document.get('species', '')} {document.get('type', '')}"
                        embedding = embeddings_model.encode([text])[0].tolist()

                        # Add embedding to the document
                        document["embedding"] = embedding

                        # Index document into Elasticsearch
                        es_client.index(index="pokemon", body=document)

                    except Exception as e:
                        logger.error(f"Failed to index document {filename}: {str(e)}")

    except Exception as e:
        logger.error(f"Failed to seed ElasticSearch with sample documents: {str(e)}")


def init_es_index():
    retries = 5
    while retries > 0:
        try:
            if not es_client.indices.exists(index="pokemon"):
                mappings = load_mappings()
                es_client.indices.create(index="pokemon", body=mappings)
            return  # Exit if initialization is successful
        except Exception as e:
            retries -= 1
            logger.error(
                f"Failed to initialize Elasticsearch index. Retries left: {retries}. Error: {str(e)}"
            )
            time.sleep(5)  # Wait before retrying
    logger.error("Failed to initialize Elasticsearch after several retries. Exiting.")
    exit(1)  # Exit the application if unable to initialize


def init_embeddings_model():
    logger.info("Initializing embeddings_model")
    global embeddings_model
    if embeddings_model is None:
        embeddings_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
        logger.info("Embeddings_model initialized!")

def get_embeddings_model():
    global embeddings_model
    if embeddings_model is None:
        init_embeddings_model()
    return embeddings_model

def setup_logging():
    # Retrieve the logging level from the environment variable
    log_level_str = os.getenv("LOG_LEVEL", "DEBUG").upper()

    # Map string log level to logging level constants
    log_level = getattr(logging, log_level_str, logging.DEBUG)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def init_core_services():
    setup_logging()
    init_embeddings_model()
    init_es_index()
    seed_database_with_sample_data()
