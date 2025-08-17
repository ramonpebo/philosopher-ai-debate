# main.py
from philosophy_ai.philosopher import PhilosopherAgent
from philosophy_ai.debate import DebateManager

def main():
    
    # Define philosophers
    plato = PhilosopherAgent(
        name="Plato",
        philosophy_focus="idealism and forms",
        ollama_model="gpt-oss",
        opponents=["Nietzsche", "Kant"]
    )

    nietzsche = PhilosopherAgent(
        name="Nietzsche",
        philosophy_focus="existentialism and will to power",
        ollama_model="gpt-oss",
        opponents=["Plato", "Kant"]
    )

    kant = PhilosopherAgent(
        name="Kant",
        philosophy_focus="categorical imperative and ethics",
        ollama_model="gpt-oss",
        opponents=["Plato", "Nietzsche"]
    )

    # Create debate manager
    debate = DebateManager(
        topic="What is the true source of human morality?",
        philosophers=[plato, nietzsche, kant],
        max_rounds=4,
        transcript_file="debate_transcript.txt"
    )

    # Run the debate
    debate.run_dynamic_debate()

if __name__ == "__main__":
    main()