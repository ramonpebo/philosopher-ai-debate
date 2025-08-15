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

    def __init__(self, ollama_model: str, philosopher_a_name: str, philosopher_a_context: str, philosopher_b_name: str, philosopher_b_context: str):

        self.philosopher_a_name = philosopher_a_name
        self.philosopher_b_name = philosopher_b_name
        self.philosopher_a_context = philosopher_a_context
        self.philosopher_b_context = philosopher_b_context

        self.model = OpenAIModel(
            model_name= ollama_model, provider=OpenAIProvider(base_url='http://localhost:11434/v1')
        )

        # Agent to decide the next action
        self.agent = Agent(
            self.model,
            output_type=ModeratorResponse,
            system_prompt=(
                "You are a debate moderator. Your role is to manage the debate between two philosophers. "
                f"The philosophers are {self.philosopher_a_name} (philosopher_a) who speacialises in {self.philosopher_a_context} and {self.philosopher_b_name} (philosopher_b) who speacialises in {self.philosopher_b_context}."
                "You will receive the current transcript and the last arguments from both philosophers. "
                "Analyze the debate and decide the next action. Possible actions include: "
                f"'ask_philosopher_a', 'ask_philosopher_b', 'move_to_closing'. "
                "Respond ONLY in JSON with one field: 'action'."
            )
        )

        # Agent to summarize arguments
        self.summary_agent = Agent(
            self.model,
            output_type=ModeratorSummaryResponse,
            system_prompt=(
                "You are a debate moderator. Summarize the following argument in one or two sentences for the audience. "
                "Then provide commentary to make the debate more engaging. "
                f"The philosophers are {self.philosopher_a_name} and {self.philosopher_b_name}. "
                "Respond ONLY in JSON with three fields: 'summary' and 'commentary'."
            )
        )

        # Agent for generating the introduction
        self.introduction_agent = Agent(
            self.model,
            output_type=str,  # The introduction will be plain text
            system_prompt=(
                "You are a debate moderator. Create an engaging and dynamic introduction for a debate. "
                f"The philosophers are {self.philosopher_a_name} and {self.philosopher_b_name}. "
                "The introduction should:\n"
                "1. Present the topic in an exciting and thought-provoking way.\n"
                "2. Introduce the two philosophers with flair, highlighting their expertise and perspectives.\n"
                "3. Set expectations for the audience.\n"
                "Respond with a single paragraph."
            )
        )

    def decide_next_action(self, transcript: str, last_argument_a: str, last_argument_b: str) -> str:
        """Decides the next action based on the current state of the debate."""
        prompt = (
            f"Transcript so far:\n{transcript}\n\n"
            f"Last argument from Philosopher A: {last_argument_a}\n"
            f"Last argument from Philosopher B: {last_argument_b}\n"
            "What should be the next action?"
        )
        try:
            response = self.agent.run_sync(prompt)
            return response.output.action
        except Exception as e:
            print(f"Error in ModeratorAgent: {e}")
            return "move_to_closing"  # Default action to move to closing in case of an error
        
    def introduce_debate(self, topic: str, philosopher_a_name: str, philosopher_a_context: str, philosopher_b_name: str, philosopher_b_context: str) -> str:
        """Generates a dynamic and engaging introduction for the debate using the LLM."""
        prompt = (
            f"The topic of the debate is: '{topic}'. "
            f"Introduce the two philosophers by name and area of expertise.\n"
        )

        try:
            response = self.introduction_agent.run_sync(prompt)
            return response.output  # Assuming the LLM returns a plain text introduction
        except Exception as e:
            print(f"Error in ModeratorAgent while generating introduction: {e}")
            return (
                f"Welcome to today's debate on '{topic}'. "
                f"We have {philosopher_a_name}, an expert in {philosopher_a_context}, and {philosopher_b_name}, an expert in {philosopher_b_context}. "
                f"Let the debate begin!"
            )
        
    def provide_input(self, action: str, philosopher_a_name: str, philosopher_b_name: str) -> str:
        """Generates a moderator input explaining the next step."""
        inputs = {
            "ask_philosopher_a": f"Now, {philosopher_a_name} will present their argument.",
            "ask_philosopher_b": f"Now, {philosopher_b_name} will present their argument.",
            "move_to_closing": "We are moving to the closing statements. Each philosopher will summarize their position.",
        }
        return inputs.get(action, "The debate is progressing.")

    def analyze_argument(self, argument: str) -> dict:
        """Analyzes the last argument and provides a summary and commentary."""

        prompt = (
            f"Analyze the following argument:\n\n"
            f"{argument}\n\n"
            "1. Summarize the argument in one or two sentences for the audience.\n"
            "2. Provide commentary to make the debate more engaging.\n"
            "Respond ONLY in JSON with two fields: 'summary' and 'commentary'."
        )

        try:
            response = self.summary_agent.run_sync(prompt)
            print(f"Raw response from summary agent: {response}")  # Debugging line
            return {
                "summary": response.output.summary,
                "commentary": response.output.commentary,
            }
        except Exception as e:
            print(f"Error in ModeratorAgent while analyzing argument: {e}")
            return {
                "summary": "The argument was insightful but could not be summarized at this time.",
                "commentary": "The debate is heating up! Let's see what happens next.",
            }