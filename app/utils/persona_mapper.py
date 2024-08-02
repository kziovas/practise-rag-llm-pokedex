from app.enums import Personas


class _PersonaPromptMapper:
    def __init__(self):
        # Define prompts for each persona
        self.persona_prompts = {
            Personas.PROFESSOR: "Answer this as Professor Oak, a Pokémon scientist and enthusiast. Focus all answers around Pokemon."
            # Add more personas and their prompts here as needed
        }

    def get_persona_prompt(self, persona):
        # Check if persona is valid
        if persona in self.persona_prompts:
            return self.persona_prompts[persona]
        else:
            return None  # Return None or handle invalid persona case


# Singleton instance
PersonaPromptMapper = _PersonaPromptMapper()
