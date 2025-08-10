from pydantic import BaseModel
from pydantic_ai import Agent

# Structure response
class DebateResponse(BaseModel):
    argument: str
    counter_argument: str
    conclusion: str

# Basic philosopher Agent
agent = Agent(
    'huggingface:openai/gpt-oss-120b',
    output_type=DebateResponse,
    system_prompt="You are a leading expert in Dovtoyesky's philosophy. You are going to receive affirmation from a student. I need you to answer them as if you were Dovtoyesky himself, " \
                  "using his philosophical insights and style." \
                  "Always respond in JSON with fields: argument, counter_argument, conclusion.",
)

# Example usage
result = agent.run_sync("Is existence prior to essence?")

# Extract the structured DebateResponse
debate_response = result.output

print("Argument: ", debate_response.argument, "\n")
print("Counter Argument: ", debate_response.counter_argument, "\n")
print("Conclusion: ", debate_response.conclusion, "\n")
