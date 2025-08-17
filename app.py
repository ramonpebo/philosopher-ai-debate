import streamlit as st
import time
from typing import Dict, List
import io
import sys

# Assuming your project structure is:
# - project_root/
#   - philosophy_ai/
#     - philosopher.py
#     - debate.py
#   - app.py (this file)
# The imports below assume you have added the project_root to your Python path or are running from it.
from philosophy_ai.philosopher import PhilosopherAgent
from philosophy_ai.debate import DebateManager

# Set up the page configuration
st.set_page_config(
    page_title="Philosophical Debate Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Streamlit UI Components ---

# Main header
st.title("🏛️ Philosophical Debate Simulator")
st.markdown("Use this dashboard to configure and run a debate between AI philosophers powered by `pydantic-ai`.")

# --- Debate Configuration Form ---

# Topic input
st.header("📝 Debate Topic")
topic = st.text_input(
    label="Enter the debate topic:",
    value="What is the true source of human morality?"
)

# Max rounds input
max_rounds = st.number_input(
    label="Maximum Number of Rounds",
    min_value=1,
    max_value=20,
    value=4,
    step=1
)

# Sidebar for managing philosophers
st.sidebar.header("👤 Philosophers")
st.sidebar.markdown("Define the philosophers participating in the debate.")

# Store philosophers in a session state to maintain their values across reruns
if 'philosophers' not in st.session_state:
    st.session_state.philosophers = [
        {'name': 'Plato', 'focus': 'idealism and forms'},
        {'name': 'Nietzsche', 'focus': 'existentialism and will to power'},
        {'name': 'Kant', 'focus': 'categorical imperative and ethics'},
    ]

# Display a form for each philosopher in the sidebar
for i, p in enumerate(st.session_state.philosophers):
    st.sidebar.markdown("---")
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        p['name'] = st.text_input(
            label=f"Philosopher {i+1} Name",
            value=p['name'],
            key=f"name_{i}"
        )
        p['focus'] = st.text_input(
            label="Philosophy Focus",
            value=p['focus'],
            key=f"focus_{i}"
        )
    with col2:
        st.write("") # Add some vertical space
        st.write("")
        if st.button("Remove", key=f"remove_{i}"):
            st.session_state.philosophers.pop(i)
            st.rerun()

# Button to add a new philosopher
if st.sidebar.button("➕ Add Philosopher"):
    st.session_state.philosophers.append(
        {'name': '', 'focus': ''}
    )
    st.rerun()

# --- Debate Execution ---

st.header("▶️ Run Debate")
run_debate_button = st.button("Start Debate", use_container_width=True, type="primary")

# This function will be called when the "Start Debate" button is clicked
def run_debate_simulation(topic: str, philosophers_data: List[Dict], max_rounds: int):
    """
    Runs the debate and captures the transcript output.
    """
    st.header("📜 Debate Transcript")
    st.markdown("---")

    try:
        # Create instances of the PhilosopherAgent for the debate
        philosopher_agents = []
        philosopher_names = [p['name'] for p in philosophers_data]

        for p_data in philosophers_data:
            # Automatically set all other philosophers as opponents
            opponents_list = [name for name in philosopher_names if name != p_data['name']]
            
            philosopher_agents.append(
                PhilosopherAgent(
                    name=p_data['name'],
                    philosophy_focus=p_data['focus'],
                    ollama_model="gpt-oss",
                    opponents=opponents_list
                )
            )
            
        # Initialize and run the debate manager
        debate = DebateManager(
            topic=topic,
            philosophers=philosopher_agents,
            max_rounds=max_rounds,
            transcript_file=None # Don't save to file in the app, just display
        )

        # Now, `run_dynamic_debate` returns the transcript directly
        with st.spinner('Thinking and debating...'):
            full_transcript = debate.run_dynamic_debate()
        
        st.text_area(
            label="Full Transcript",
            value=full_transcript,
            height=600,
            disabled=True,
            key="transcript_output"
        )
        st.success("Debate complete! Read the transcript above.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please ensure your backend services (like Ollama) are running and your dependencies are correctly installed.")


# Check if the button is clicked and the topic and philosophers are valid
if run_debate_button:
    if not topic:
        st.error("Please enter a debate topic.")
    elif not all(p['name'] and p['focus'] for p in st.session_state.philosophers):
        st.error("Please ensure all philosophers have a name and a focus.")
    else:
        run_debate_simulation(topic, st.session_state.philosophers, max_rounds)
