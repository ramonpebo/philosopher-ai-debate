from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider


# Philosopher response
class PhilosopherResponse(BaseModel):
    argument: str

#Load Ollama model
ollama_model = OpenAIModel(
    model_name='gpt-oss', provider=OpenAIProvider(base_url='http://localhost:11434/v1')
)

# Build prompt with phase awareness
def build_prompt(philosopher_name: str, philosophy_focus: str, phase: str) -> str:
    
    # Phase specific instructions
    phase_descriptions = {
        "opening": "Give your opening statement on the debate topic.",
        "rebuttal": "Respond directly to the opponent's last argument with a rebuttal.",
        "closing": "Provide your closing statement summarizing your stance."
    }

    # Get phase instruction
    phase_instruction = phase_descriptions.get(phase, "")
    return (
        f"You are {philosopher_name}, an expert philosopher. "
        f"Your arguments must be based entirely on {philosophy_focus}. "
        "You are debating against an opponent. "
        f"{phase_instruction} "
        "You will receive the full debate transcript so far, and also the opponent's latest argument (if any). "
        "Your task is to respond directly and keep consistency with your philosophy. "
        "Do not repeat points unnecessarily. Use quotes or references when appropriate. "
        "Keep your arguments in a single paragraph. "
        "Respond ONLY in JSON with one field: 'argument'. "
        "Do NOT include any text outside the JSON. Example: {\"argument\": \"your argument here\"}. "
        "If you do not follow this format, your answer will be rejected and you will be asked again. "
    )

# Create philosopher agents with fixed prompts for each phase
def create_agent(philosopher_name: str, philosophy_focus: str, phase: str):
    prompt = build_prompt(philosopher_name, philosophy_focus, phase)
    return Agent(
        ollama_model,
        output_type=PhilosopherResponse,
        system_prompt=prompt,
        # retries=3
    )

###################
##### DEBATE ######
###################

# Debate settings
topic = "Morality is subjective"
rounds = 3

transcript = []
last_argument_a = ""
last_argument_b = ""

print(f"--- Debate Topic: {topic} ---\n")

##### Opening statements #####
print("--- Opening Statements ---")
philosopher_a_op = create_agent("Ramon", "the works of Nietzsche", phase="opening")
philosopher_b_op = create_agent("Dilhan", "the philosophy of Immanuel Kant", phase="opening")

# Philosopher A's opening argument
try:
    result_a = philosopher_a_op.run_sync(f"Topic: {topic}")
    arg_a = result_a.output.argument
    transcript.append(f"Philosopher A (Opening Argument): {arg_a}\n")
    last_argument_a = arg_a
    print("Philosopher A - Opening Argument:", arg_a)
except UnexpectedModelBehavior as e:
    print("Philosopher A invalid output. Raw response:")
    print(e)

# Philosopher B's opening argument
try:
    result_b = philosopher_b_op.run_sync(f"Topic: {topic}")
    arg_b = result_b.output.argument
    transcript.append(f"Philosopher B (Opening Argument): {arg_b}\n")
    last_argument_b = arg_b
    print("Philosopher B - Opening Argument:", arg_b)
except UnexpectedModelBehavior as e:
    print("Philosopher B invalid output. Raw response:")
    print(e)

##### Rebuttal rounds #####
print("\n--- Rebuttal Rounds ---")

philosopher_a_reb = create_agent("Ramon", "the works of Nietzsche", phase="rebuttal")
philosopher_b_reb = create_agent("Dilhan", "the philosophy of Immanuel Kant", phase="rebuttal")

for i in range(rounds):

    # Philosopher A's rebuttal
    prompt_a = (
        f"Full transcript so far:\n{''.join(transcript)}\n\n"
        f"Opponent's last argument: {last_argument_b}"
    )
    try:
        result_a = philosopher_a_reb.run_sync(prompt_a)
        arg_a = result_a.output.argument
        transcript.append(f"Philosopher A (Rebuttal {i+1}): {arg_a}\n")
        last_argument_a = arg_a
        print(f"Philosopher A - Rebuttal {i+1}:", arg_a)
    except UnexpectedModelBehavior as e:
        print("Philosopher A invalid output. Raw response:")
        print(e)
        break

    # Philosopher B's rebuttal
    prompt_b = (
        f"Full transcript so far:\n{''.join(transcript)}\n\n"
        f"Opponent's last argument: {last_argument_a}"
    )
    try:
        result_b = philosopher_b_reb.run_sync(prompt_b)
        arg_b = result_b.output.argument
        transcript.append(f"Philosopher B (Rebuttal {i+1}): {arg_b}\n")
        last_argument_b = arg_b
        print(f"Philosopher B - Rebuttal {i+1}:", arg_b)
    except UnexpectedModelBehavior as e:
        print("Philosopher B invalid output. Raw response:")
        print(e)
        break

##### Closing Statements #####
print("\n--- Closing Statements ---")
philosopher_a_cls = create_agent("Ramon", "the works of Nietzsche", phase="closing")
philosopher_b_cls = create_agent("Dilhan", "the philosophy of Immanuel Kant", phase="closing")

closing_prompt_a = f"Full transcript so far:\n{''.join(transcript)}"

# Closing statement for Philosopher A
try:
    result_a = philosopher_a_cls.run_sync(closing_prompt_a)
    arg_a = result_a.output.argument
    transcript.append(f"Philosopher A (Closing): {arg_a}\n")
    print("Philosopher A - Closing Statement:", arg_a)
except UnexpectedModelBehavior as e:
    print("Philosopher A invalid output. Raw response:")
    print(e)

# Closing statement for Philosopher B
closing_prompt_b = f"Full transcript so far:\n{''.join(transcript)}"
try:
    result_b = philosopher_b_cls.run_sync(closing_prompt_b)
    arg_b = result_b.output.argument
    transcript.append(f"Philosopher B (Closing): {arg_b}\n")
    print("Philosopher B - Closing Statement:", arg_b)
except UnexpectedModelBehavior as e:
    print("Philosopher B invalid output. Raw response:")
    print(e)

# Print full transcript
print("\n--- Full Debate Transcript ---")
for line in transcript:
    print(line)