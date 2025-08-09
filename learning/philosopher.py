from pydantic import BaseModel
from pydantic_ai import Agent

# Structure response
class DebateResponse(BaseModel):
    argument: str
    counter_argument: str
    conclusion: str

# Basic philosopher Agent
agent = Agent(
    'huggingface:Qwen/Qwen3-235B-A22B',
    output_type=DebateResponse,
    system_prompt="You are a leading expert in Dovtoyesky's philosophy. You are going to receive questions about different topics. I need you to answer them as if you were Dovtoyesky himself, " \
                  "using his philosophical insights and style." \
                  "Always respond in JSON with fields: argument, counter_argument, conclusion.",
)

# Example usage
result = agent.run_sync("Life is meaningless.")
print(result.output)