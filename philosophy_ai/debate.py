from .agent import PhilosopherAgent

class DebateManager:
    """Manages a debate between two philosophers with multiple phases."""

    # Initialize the debate manager with topic, rounds, and model URL
    def __init__(self, topic: str, rounds: int):
        self.topic = topic
        self.rounds = rounds
        self.transcript = []
        self.last_argument_a = ""
        self.last_argument_b = ""

        # Initialize agents with phase=None (will set later)
        self.philosopher_a = PhilosopherAgent("Ramon", "the works of Nietzsche", 'gpt-oss')
        self.philosopher_b = PhilosopherAgent("Dilhan", "the philosophy of Immanuel Kant", 'gpt-oss')

    def opening_statements(self):
        """Conducts the opening statements phase of the debate."""

        print("--- Opening Statements ---")
        self.philosopher_a.set_phase("opening")
        self.philosopher_b.set_phase("opening")

        # Philosopher A's opening argument
        arg_a = self.philosopher_a.generate_argument()
        self.transcript.append(f"{self.philosopher_a.name} (Opening Argument): {arg_a}\n")
        self.last_argument_a = arg_a
        print(f"{self.philosopher_a.name} - Opening Argument:", arg_a)

        # Philosopher B's opening argument
        arg_b = self.philosopher_b.generate_argument()
        self.transcript.append(f"{self.philosopher_b.name} (Opening Argument): {arg_b}\n")
        self.last_argument_b = arg_b
        print(f"{self.philosopher_b.name} - Opening Argument:", arg_b)

    def rebuttal_rounds(self):
        """Conducts the rebuttal rounds of the debate."""

        print("\n--- Rebuttal Rounds ---")
        self.philosopher_a.set_phase("rebuttal")
        self.philosopher_b.set_phase("rebuttal")

        # Loop through the number of rounds
        for i in range(self.rounds):
            
            # Philosopher A rebuttal
            arg_a = self.philosopher_a.generate_argument(
                transcript="".join(self.transcript),
                opponent_argument=self.last_argument_b
            )
            self.transcript.append(f"{self.philosopher_a.name} (Rebuttal {i+1}): {arg_a}\n")
            self.last_argument_a = arg_a
            print(f"{self.philosopher_a.name} - Rebuttal {i+1}:", arg_a)

            # Philosopher B rebuttal
            arg_b = self.philosopher_b.generate_argument(
                transcript="".join(self.transcript),
                opponent_argument=self.last_argument_a
            )
            self.transcript.append(f"{self.philosopher_b.name} (Rebuttal {i+1}): {arg_b}\n")
            self.last_argument_b = arg_b
            print(f"{self.philosopher_b.name} - Rebuttal {i+1}:", arg_b)

    def closing_statements(self):
        """Conducts the closing statements phase of the debate."""

        print("\n--- Closing Statements ---")
        self.philosopher_a.set_phase("closing")
        self.philosopher_b.set_phase("closing")

        # Philosopher A's closing statement
        arg_a = self.philosopher_a.generate_argument(transcript="".join(self.transcript))
        self.transcript.append(f"{self.philosopher_a.name} (Closing): {arg_a}\n")
        print(f"{self.philosopher_a.name} - Closing Statement:", arg_a)

        # Philosopher B's closing statement
        arg_b = self.philosopher_b.generate_argument(transcript="".join(self.transcript))
        self.transcript.append(f"{self.philosopher_b.name} (Closing): {arg_b}\n")
        print(f"{self.philosopher_b.name} - Closing Statement:", arg_b)

    def run_debate(self):
        """Runs the full debate process."""
        
        print(f"--- Debate Topic: {self.topic} ---\n")
        self.opening_statements()
        self.rebuttal_rounds()
        self.closing_statements()

        print("\n--- Full Debate Transcript ---")
        for line in self.transcript:
            print(line)
