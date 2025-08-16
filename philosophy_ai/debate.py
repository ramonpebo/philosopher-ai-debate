import os
from .philosopher import PhilosopherAgent
from .moderator import ModeratorAgent

class DebateManager:
    """Manages a debate dynamically based on the moderator's decisions."""

    def __init__(self, topic: str, philosophers: list, max_rounds: int = 6, transcript_file: str = None):
        
        self.topic = topic
        self.philosophers = philosophers
        self.transcript = []
        self.last_arguments = {philosopher.name: "" for philosopher in philosophers}
        self.speakers_order = ""
        self.round_count = 0
        self.max_rounds = max_rounds
        self.transcript_file = transcript_file

        # Initialize the moderator agent with all philosophers
        self.moderator = ModeratorAgent(
            ollama_model='gpt-oss',
            philosophers=philosophers
        )

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
        introduction = self.moderator.introduce_debate(self.topic)
        print(f"Moderator: {introduction}")
        self.transcript.append(f"Moderator: {introduction}\n")

        print(f"\n--- Debate Topic: {self.topic} ---\n")

        # Opening statements for all philosophers
        for philosopher in self.philosophers:
            philosopher.set_phase("opening")
            opening_statement = philosopher.generate_argument()
            self.last_arguments[philosopher.name] = opening_statement
            self.speakers_order += f"{philosopher.name}, "
            print("Speakers Order:", self.speakers_order)
            self.transcript.append(f"{philosopher.name} (Opening): {opening_statement}\n")
            print(f"{philosopher.name} - Opening Statement:", opening_statement)
            

        # Main debate rounds
        print("\n--- Main Debate ---")

        for philosopher in self.philosophers:
            # Set rebuttal phase for each philosopher
            philosopher.set_phase("rebuttal")

        while True:
            # Check if the maximum number of rounds has been reached
            if self.round_count > self.max_rounds:
                print("\n--- Maximum Rounds Reached ---")
                break
            else:
                # Ask the moderator for the next action
                action = self.moderator.decide_next_action(
                    last_arguments=self.last_arguments,
                    speakers_order=self.speakers_order
                )

                # Moderator provides input on the next action
                moderator_input = self.moderator.provide_input(action)
                print(f"Moderator: {moderator_input}")
                self.transcript.append(f"Moderator: {moderator_input}\n")

                if action == "move_to_closing":
                    break

                # Philosopher selected by the moderator provides an argument
                if action.startswith("ask_philosopher_"):
                    selected_philosopher_name = action.replace("ask_philosopher_", "")
                    selected_philosopher = next(
                        (p for p in self.philosophers if p.name == selected_philosopher_name), None
                    )
                    print(f"Selected Philosopher: {selected_philosopher_name}")

                    if selected_philosopher:
                        # Combine arguments from all opponents
                        opponent_arguments = "\n".join(
                            f"{opponent_name}: {self.last_arguments[opponent_name]}" for opponent_name in selected_philosopher.opponents
                        )

                        # Generate the argument
                        argument = selected_philosopher.generate_argument(
                            opponents_argument=opponent_arguments
                        )

                        self.transcript.append(f"{selected_philosopher.name}: {argument}\n")
                        self.last_arguments[selected_philosopher.name] = argument
                        self.speakers_order += f"{selected_philosopher.name}, "
                        print("Speakers Order:", self.speakers_order)
                        print(f"{selected_philosopher.name}:", argument)

                        # Provide the argument to the moderator for analysis
                        analysis = self.moderator.analyze_argument(selected_philosopher.name, argument)
                        print(f"Moderator Summary of {selected_philosopher.name}'s Argument:", analysis['summary'])
                        print(f"Moderator Commentary of {selected_philosopher.name}'s Argument:", analysis['commentary'])
                        self.transcript.append(f"Moderator: {analysis['summary']}\n")
                        self.transcript.append(f"Moderator: {analysis['commentary']}\n")

                self.round_count += 1

        # Closing statements
        print("\n--- Closing Statements ---")
        for philosopher in self.philosophers:
            philosopher.set_phase("closing")
            # Combine arguments from all opponents
            opponent_arguments = "\n".join(
                f"{opponent_name}: {self.last_arguments[opponent_name]}" for opponent_name in selected_philosopher.opponents
            )
            closing_statement = philosopher.generate_argument(opponents_argument = opponent_arguments)
            self.transcript.append(f"{philosopher.name} (Closing): {closing_statement}\n")
            print(f"{philosopher.name} - Closing Statement:", closing_statement)

        print("\n--- Debate Ended ---")

        # Print the full transcript
        print("\n--- Full Debate Transcript ---")
        for line in self.transcript:
            print(line)

        # Save the transcript to a file if specified
        self.save_transcript()