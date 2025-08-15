from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

class PhilosopherResponse(BaseModel):
    argument: str


class PhilosopherAgent:
    """A philosopher agent that can debate in different phases."""

    def __init__(self, name: str, philosophy_focus: str, ollama_model: str, opponent_name: str):

        self.name = name
        self.philosophy_focus = philosophy_focus
        self.opponent_name = opponent_name

        self.model = OpenAIModel(
            model_name=ollama_model, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )
        self.agent = None  # Will be set on phase change

    # Build prompt with phase awareness
    def build_prompt(self, phase: str, transcript: str = "", opponent_argument: str = "") -> str:
        phase_descriptions = {
            "opening": "Give your opening statement on the debate topic.",
            "rebuttal": "Respond directly to the opponent's last argument with a rebuttal.",
            "closing": "Provide your closing statement summarizing your stance."
        }
        phase_instruction = phase_descriptions.get(phase, "")

        agent_context = (
            f"You are {self.name}, an expert philosopher. "
            f"Your arguments must be based entirely on {self.philosophy_focus}. "
            f"You are debating against {self.opponent_name}. "
            f"{phase_instruction} "
            "Do not repeat points unnecessarily. Use quotes or references when appropriate. Respond to your opponent by name."
            "Keep your arguments in a single paragraph. "
            "Respond ONLY in JSON with one field: 'argument'. "
            "Do NOT include any text outside the JSON. Example: {\"argument\": \"your argument here\"}. "
            "If you do not follow this format, your answer will be rejected and you will be asked again."
        )

        if phase in ["rebuttal", "closing"]:
            agent_context += f"\nFull transcript so far:\n{transcript}"
            if phase == "rebuttal":
                agent_context += f"\nOpponent's last argument: {opponent_argument}"

        return agent_context

    # Set the agent for the current phase
    def set_phase(self, phase: str):
        agent_context = self.build_prompt(phase)
        self.agent = Agent(
            self.model,
            retries=3,
            output_type=PhilosopherResponse,
            system_prompt=agent_context
        )
        self.phase = phase

    # Generate argument for the current phase
    def generate_argument(self, transcript: str = "", opponent_argument: str = "") -> str:
        if self.agent is None:
            raise RuntimeError("Agent not initialized for phase. Call set_phase first.")

        # Build prompt including transcript and opponent argument for rebuttal/closing
        prompt = self.build_prompt(self.phase, transcript, opponent_argument)
        try:
            response = self.agent.run_sync(prompt)
            return response.output.argument
        except UnexpectedModelBehavior as e:
            print(f"{self.name} invalid output in phase '{self.phase}'. Raw response:")
            print(e)
            raise
