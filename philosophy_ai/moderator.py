from typing import Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

class ModeratorResponse(BaseModel):
    action: str  # e.g., "trigger_phase", "end_debate"

class ModeratorSummaryResponse(BaseModel):
    summary: Optional[str] # The summary of the argument
    commentary: Optional[str]  # Engaging commentary from the moderator

class ModeratorResponseIntro(BaseModel):
    introduction: str  # intro text for the debate

class ModeratorAgent:
    """A moderator agent that orchestrates the debate dynamically and provides inputs."""

    def __init__(self, ollama_model: str, philosophers: list):

        self.philosophers = philosophers

        # Build a dynamic description of all philosophers
        self.philosopher_descriptions = ", ".join(
            f"{philosopher.name} (specializes in {philosopher.philosophy_focus})" for philosopher in philosophers
        )

        self.model = OpenAIModel(
            model_name=ollama_model, 
            provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )

        # Agent to decide the next action
        self.agent = Agent(
            self.model,
            retries=3,
            output_type=ModeratorResponse,
            system_prompt=(
                "You are a debate moderator. Your role is to select the next speaker. "
                f"The philosophers are: {self.philosopher_descriptions}. "
                "You must choose a philosopher to speak from the available list. "
                "Do NOT choose the same philosopher who just spoke. "
                "Respond ONLY in JSON with one field: 'action'. "
                "The value of 'action' must be in the format 'ask_philosopher_<name>'.\n\n"
                "Use the exact name provided in the list (e.g., 'Plato', not 'plato' or 'Platon').\n\n"
            )
        )

        # Agent to summarize arguments
        self.summary_agent = Agent(
            self.model,
            retries=3,
            output_type=ModeratorSummaryResponse,
            system_prompt=(
                "You are a debate moderator. Summarize the following argument in one or two sentences for the audience. "
                "Then provide commentary to make the debate more engaging. "
                f"The philosophers are: {self.philosopher_descriptions}. "
                "Respond ONLY in JSON with two fields: 'summary' and 'commentary'."
            )
        )

        # Agent for generating the introduction
        self.introduction_agent = Agent(
        self.model,
        retries=3,
        output_type=ModeratorResponseIntro,
        system_prompt=(
            "You are a debate moderator. Create an engaging and dynamic introduction for a debate. "
            f"The philosophers are: {self.philosopher_descriptions}. "
            "The introduction should:\n"
            "1. Present the topic in an exciting and thought-provoking way.\n"
            "2. Introduce the philosophers with flair, highlighting their expertise and perspectives.\n"
            "3. Set expectations for the audience.\n"
            "Respond ONLY in JSON with one field: 'introduction'."
            )
        )

    def decide_next_action(self, last_arguments: dict, last_speaker: str) -> str:
        """Decides the next action based on the current state of the debate."""

        # Explicitly state the last speaker to the LLM
        last_speaker_text = f"The last speaker was {last_speaker}." if last_speaker else ""
        
        # Filter available speakers
        available_philosophers = [p.name for p in self.philosophers if p.name != last_speaker]
        available_philosophers_text = ", ".join(available_philosophers)

        prompt = (
            f"Current status: The debate has progressed. {last_speaker_text}\n"
            f"The available philosophers to speak are: {available_philosophers_text}\n"
            f"Last arguments from all philosophers:\n" + "\n".join(
                f"{name}: {argument}" for name, argument in last_arguments.items()
            ) + "\n\n"
            "Who should speak next? Choose only from the available philosophers."
        )

        try:
            response = self.agent.run_sync(prompt)
            return response.output.action
        except Exception as e:
            print(f"Error in ModeratorAgent: {e}")
            # This fallback is crucial. If the LLM gives an invalid response,
            # you must have a way to recover. For instance, just pick the first one.
            return f"ask_philosopher_{available_philosophers[0]}"
        
    def introduce_debate(self, topic: str) -> str:
        """Generates a dynamic and engaging introduction for the debate using the LLM."""

        prompt = (
            f"The topic of the debate is: '{topic}'. "
            f"Introduce the philosophers: {self.philosopher_descriptions}. "
            "Make it engaging and thought-provoking."
        )

        try:
            response = self.introduction_agent.run_sync(prompt)
            return response.output.introduction
        except Exception as e:
            print(f"Error in ModeratorAgent while generating introduction: {e}")
            return (
                f"Welcome to today's debate on '{topic}'. "
                f"We have {self.philosopher_descriptions}. "
                f"Let the debate begin!"
            )
        
    def provide_input(self, action: str, philosopher_name: Optional[str] = None) -> str:
        """Generates a moderator input explaining the next step."""

        if action.startswith("ask_philosopher_"):
            philosopher_name = action.replace("ask_philosopher_", "")
            return f"Now, {philosopher_name} will present their argument."
        elif action == "move_to_closing":
            return "We are moving to the closing statements. Each philosopher will summarize their position."
        else:
            return "The debate is progressing."

    def analyze_argument(self, philosopher_name: str, argument: str) -> dict:
        """Analyzes the last argument and provides a summary and commentary."""

        prompt = (
            f"Analyze the following argument from {philosopher_name}:\n\n"
            f"{argument}\n\n"
            "1. Summarize the argument in one or two sentences for the audience.\n"
            "2. Provide commentary to make the debate more engaging.\n"
            "Respond ONLY in JSON with two fields: 'summary' and 'commentary'."
        )

        try:
            response = self.summary_agent.run_sync(prompt)
            return {
                "summary": response.output.summary,
                "commentary": response.output.commentary,
            }
        
        except Exception as e:
            print(f"Error in ModeratorAgent while analyzing argument: {e}")
            return {
                "summary": f"The argument from {philosopher_name} was insightful but could not be summarized at this time.",
                "commentary": "The debate is heating up! Let's see what happens next.",
            }