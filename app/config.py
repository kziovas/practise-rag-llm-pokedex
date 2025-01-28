import os


LLM_MODEL_VERSION = os.environ.get("LLM_MODEL_VERSION", "llama2")
ELASTICSEARCH_URI = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
LLAMA_BASE_URL = os.environ.get("LLAMA_BASE_URL", "http://ollama:11434")
MAPPINGS_PATH = os.path.join(os.path.dirname(__file__), "mappings.json")
POKEMON_PATH = os.path.join(os.path.dirname(__file__), "mappings.json")
MAX_LLM_INPUT_LENGTH = os.environ.get("MAX_LLM_INPUT_LENGTH", 20)
MAX_LLM_INPUT_SENTENCES = os.environ.get("MAX_LLM_INPUT_SENTENCES", 4)

