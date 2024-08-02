from langchain_community.llms.ollama import Ollama
from app.config import (
    LLM_MODEL_NAME,
    MAX_LLM_INPUT_LENGTH,
    MAX_LLM_INPUT_SENTENCES,
    LLAMA_BASE_URL,
)
from app.utils.text_processing import TextProcessing
from app.utils.persona_mapper import PersonaPromptMapper
from app.enums import Personas


class LLMAssistant:
    def __init__(
        self, persona: Personas = Personas.PROFESSOR, model_name: str = LLM_MODEL_NAME
    ):
        self.persona = persona
        self.persona_prompt = PersonaPromptMapper.get_persona_prompt(persona)
        self.model = Ollama(name=model_name, base_url=LLAMA_BASE_URL)
        self.previous_accumulated_text = ""  # Track previous accumulated text

    def process(self, question: str):
        accumulated_text = ""  # Initialize accumulated text

        processed_question = TextProcessing.truncate_text(
            question,
            max_words=MAX_LLM_INPUT_LENGTH,
            max_sentences=MAX_LLM_INPUT_SENTENCES,
        )
        input_text = f"Persona:'{self.persona_prompt}',Prompt: '{processed_question}'"

        for chunk in self.model.stream(input_text):
            accumulated_text += chunk

            # Check if we have formed complete sentences
            sentences = accumulated_text.split(". ")  # Split by sentences

            # Join sentences with proper punctuation
            complete_sentences = []
            for i in range(len(sentences) - 1):
                if i == 0:
                    complete_sentences.append(sentences[i] + ". ")  # Include the period
                else:
                    complete_sentences.append(sentences[i] + ". ")  # Include the period

            # Yield the current state of accumulated text (up to complete sentences)
            yield "".join(complete_sentences)

            # Check for stream reset (from non-empty to empty accumulated text)
            if self.previous_accumulated_text and not accumulated_text.strip():
                self.previous_accumulated_text = ""
                break  # Exit the generator if stream reset detected

            self.previous_accumulated_text = (
                accumulated_text  # Update previous accumulated text
            )

        # After finishing all chunks, yield any remaining accumulated text
        yield accumulated_text


DefaultAssistant = LLMAssistant()
