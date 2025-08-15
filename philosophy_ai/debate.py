import os
from .philosopher import PhilosopherAgent
from .moderator import ModeratorAgent

class DebateManager:
    """Manages a debate dynamically based on the moderator's decisions."""

    def __init__(self, topic: str, philosopher_a_name: str, philosopher_a_context: str, philosopher_b_name: str, philosopher_b_context: str, max_rounds: int = 6, transcript_file: str = None):
        self.topic = topic
        self.transcript = []
        self.last_argument_a = ""
        self.last_argument_b = ""
        self.round_count = 0  # Track the number of rounds
        self.max_rounds = max_rounds  # Maximum number of rounds
        self.transcript_file = transcript_file  # Assign transcript_file to an instance attribute

        # Initialize philosopher agents with their names and contexts
        self.philosopher_a = PhilosopherAgent(philosopher_a_name, philosopher_a_context, 'gpt-oss', philosopher_b_name)
        self.philosopher_b = PhilosopherAgent(philosopher_b_name, philosopher_b_context, 'gpt-oss', philosopher_a_name)
        # Initialize the moderator agent
        self.moderator = ModeratorAgent('gpt-oss', philosopher_a_name, philosopher_a_context, philosopher_b_name, philosopher_b_context)

    def save_transcript(self):
        """Saves the transcript to a file if a file path is provided."""
        if self.transcript_file:
            try:
                with open(self.transcript_file, 'w', encoding='utf-8') as file:
                    file.writelines(self.transcript)
                print(f"Transcript saved to {self.transcript_file}")
            except Exception as e:
                print(f"Error saving transcript: {e}")
    
    def run_dynamic_debate(self):
        """Runs the debate dynamically based on the moderator's decisions."""

        # Moderator introduces the debate
        introduction = self.moderator.introduce_debate(
            topic=self.topic,
            philosopher_a_name=self.philosopher_a.name,
            philosopher_a_context=self.philosopher_a.philosophy_focus,
            philosopher_b_name=self.philosopher_b.name,
            philosopher_b_context=self.philosopher_b.philosophy_focus
        )
        print(f"Moderator: {introduction}")
        self.transcript.append(f"Moderator: {introduction}\n")

        print(f"\n--- Debate Topic: {self.topic} ---\n")

        # Set initial phase for philosophers
        self.philosopher_a.set_phase("opening")
        self.philosopher_b.set_phase("opening")

        # Philosopher A's opening statement
        opening_a = self.philosopher_a.generate_argument()
        self.transcript.append(f"{self.philosopher_a.name} (Opening): {opening_a}\n")
        print(f"{self.philosopher_a.name} - Opening Statement:", opening_a)

        # Philosopher B's opening statement
        opening_b = self.philosopher_b.generate_argument()
        self.transcript.append(f"{self.philosopher_b.name} (Opening): {opening_b}\n")
        print(f"{self.philosopher_b.name} - Opening Statement:", opening_b)

        # Main debate rounds
        print("\n--- Main Debate ---")
        self.philosopher_a.set_phase("rebuttal")
        self.philosopher_b.set_phase("rebuttal")

        while True:
            # Check if the maximum number of rounds has been reached
            if self.round_count >= self.max_rounds:
                print("\n--- Maximum Rounds Reached ---")
                action = "move_to_closing"
            else:
                # Ask the moderator for the next action
                action = self.moderator.decide_next_action(
                    transcript="".join(self.transcript),
                    last_argument_a=self.last_argument_a,
                    last_argument_b=self.last_argument_b
                )

            # Moderator analyzes the last argument
            if action == "ask_philosopher_a" and self.last_argument_b:
                analysis = self.moderator.analyze_argument(self.last_argument_b)
                summary = f"Moderator Summary of {self.philosopher_b.name}'s Argument: {analysis['summary']}"
                commentary = f"Moderator Commentary: {analysis['commentary']}"
                print(summary)
                print(commentary)
                self.transcript.append(f"Moderator: {summary}\n")
                self.transcript.append(f"Moderator: {commentary}\n")
            elif action == "ask_philosopher_b" and self.last_argument_a:
                analysis = self.moderator.analyze_argument(self.last_argument_a)
                summary = f"Moderator Summary of {self.philosopher_a.name}'s Argument: {analysis['summary']}"
                commentary = f"Moderator Commentary: {analysis['commentary']}"
                print(summary)
                print(commentary)
                self.transcript.append(f"Moderator: {summary}\n")
                self.transcript.append(f"Moderator: {commentary}\n")

            # Moderator provides input
            moderator_input = self.moderator.provide_input(action, self.philosopher_a.name, self.philosopher_b.name)
            print(f"Moderator: {moderator_input}")
            self.transcript.append(f"Moderator: {moderator_input}\n")

            if action == "ask_philosopher_a":
                # Ask Philosopher A for an argument
                arg_a = self.philosopher_a.generate_argument(
                    transcript="".join(self.transcript),
                    opponent_argument=self.last_argument_b
                )
                self.transcript.append(f"{self.philosopher_a.name}: {arg_a}\n")
                self.last_argument_a = arg_a
                print(f"{self.philosopher_a.name}:", arg_a)
                self.round_count += 1  # Increment the round count

            elif action == "ask_philosopher_b":
                # Ask Philosopher B for an argument
                arg_b = self.philosopher_b.generate_argument(
                    transcript="".join(self.transcript),
                    opponent_argument=self.last_argument_a
                )
                self.transcript.append(f"{self.philosopher_b.name}: {arg_b}\n")
                self.last_argument_b = arg_b
                print(f"{self.philosopher_b.name}:", arg_b)
                self.round_count += 1  # Increment the round count

            elif action == "move_to_closing":
                # Combine closing statements and end debate
                print("\n--- Closing Statements ---")
                self.philosopher_a.set_phase("closing")
                self.philosopher_b.set_phase("closing")

                arg_a = self.philosopher_a.generate_argument(transcript="".join(self.transcript))
                self.transcript.append(f"{self.philosopher_a.name} (Closing): {arg_a}\n")
                print(f"{self.philosopher_a.name} - Closing Statement:", arg_a)

                arg_b = self.philosopher_b.generate_argument(transcript="".join(self.transcript))
                self.transcript.append(f"{self.philosopher_b.name} (Closing): {arg_b}\n")
                print(f"{self.philosopher_b.name} - Closing Statement:", arg_b)

                print("\n--- Debate Ended ---")
                break

        # Print the full transcript
        print("\n--- Full Debate Transcript ---")
        for line in self.transcript:
            print(line)

        # Save the transcript to a file if specified
        self.save_transcript()