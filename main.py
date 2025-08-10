from philosophy_ai.debate import DebateManager

def main():
    topic = "Morality is subjective"
    rounds = 3

    debate = DebateManager(topic, rounds)
    debate.run_debate()

if __name__ == "__main__":
    main()
