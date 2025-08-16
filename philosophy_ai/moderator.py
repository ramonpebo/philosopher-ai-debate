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

class ModeratorAgent:
    """A moderator agent that orchestrates the debate dynamically and provides inputs."""

    def __init__(self, ollama_model: str, philosophers: list):

        self.philosophers = philosophers

        # Build a dynamic description of all philosophers
        philosopher_descriptions = ", ".join(
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
            "You are a debate moderator. Your role is to manage the debate between multiple philosophers. "
            f"The philosophers are: {philosopher_descriptions}. "
            "You will receive the current transcript and the last arguments from all philosophers. "
            "Analyze the debate and decide the next action. Possible actions include: "
            "'ask_philosopher_<name>', 'move_to_closing'. "
            "Respond ONLY in JSON with one field: 'action'.\n\n"
            "RULES:\n"
            f"- The speaking order must strictly follow round-robin, for example: Speaker 1, then Speaker 2 and lastly Speaker 3. If we only have 3 speakers, then you will move back to Speaker 1 to create a loop.\n"
            "- Never let the same philosopher speak twice in a row.\n"
            "- Always pick the next philosopher in the cycle after the last one who spoke.\n"
            "- Only output 'move_to_closing' if the debate has clearly ended.\n\n"
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
                f"The philosophers are: {philosopher_descriptions}. "
                "Respond ONLY in JSON with two fields: 'summary' and 'commentary'."
            )
        )

        # Agent for generating the introduction
        self.introduction_agent = Agent(
        self.model,
        retries=3,
        system_prompt=(
            "You are a debate moderator. Create an engaging and dynamic introduction for a debate. "
            f"The philosophers are: {philosopher_descriptions}. "
            "The introduction should:\n"
            "1. Present the topic in an exciting and thought-provoking way.\n"
            "2. Introduce the philosophers with flair, highlighting their expertise and perspectives.\n"
            "3. Set expectations for the audience.\n"
            "Respond ONLY in JSON with one field: 'introduction'."
            )
        )

    def decide_next_action(self, last_arguments: dict, speakers_order: str) -> str:
        """Decides the next action based on the current state of the debate."""

        # Build a dynamic prompt with the last arguments of all philosophers
        last_arguments_text = "\n".join(
            f"Last argument from {name}: {argument}" for name, argument in last_arguments.items()
        )

        prompt = (
            f"{last_arguments_text}\n"
            f"Debate speakers order: {speakers_order}\n"
            "What should be the next action?"
        )
        try:
            response = self.agent.run_sync(prompt)
            return response.output.action
        except Exception as e:
            print(f"Error in ModeratorAgent: {e}")
            return "move_to_closing"  # Default action to move to closing in case of an error
        
    def introduce_debate(self, topic: str) -> str:
        """Generates a dynamic and engaging introduction for the debate using the LLM."""

        philosopher_descriptions = ", ".join(
            f"{philosopher.name} (specializes in {philosopher.philosophy_focus})" for philosopher in self.philosophers
        )

        prompt = (
            f"The topic of the debate is: '{topic}'. "
            f"Introduce the philosophers: {philosopher_descriptions}. "
            "Make it engaging and thought-provoking."
        )

        try:
            response = self.introduction_agent.run_sync(prompt)
            return response.output
        except Exception as e:
            print(f"Error in ModeratorAgent while generating introduction: {e}")
            return (
                f"Welcome to today's debate on '{topic}'. "
                f"We have {philosopher_descriptions}. "
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