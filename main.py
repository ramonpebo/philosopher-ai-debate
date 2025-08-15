from philosophy_ai.debate import DebateManager

def main():
    topic = "Morality is subjective"
    # Philosophers' names and contexts
    philosopher_a_name = "Ramon"
    philosopher_a_context = "the works of Nietzsche"
    philosopher_b_name = "Dilhan"
    philosopher_b_context = "the philosophy of Immanuel Kant"

    debate = DebateManager(topic, philosopher_a_name, philosopher_a_context, philosopher_b_name, philosopher_b_context, max_rounds=2)
    debate.run_dynamic_debate()

if __name__ == "__main__":
    main()
º