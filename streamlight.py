import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from math import ceil

# Initialize session state for questions and current page
if 'questions' not in st.session_state:
    st.session_state.questions = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'  # Default to main page


def display_question_card(question: Dict, index: int, container) -> None:
    """Display an individual question card with interactive elements."""
    try:
        # Extract necessary details
        category = question.get('category', 'Unknown')
        difficulty = question.get('difficulty', 'Unknown')
        context = question.get('context', '').strip()
        question_text = question.get('question', '')
        options = question.get('options', {})

        # Start container
        with container:
            st.markdown(f"""
                <div style='
                    border: 2px solid rgba(255, 255, 255, 0.8);
                    border-radius: 10px;
                    padding: 1.5rem;
                    margin-bottom: 1rem;
                '>
                    <h3>Question {index + 1}</h3>
                    <p><strong>Category:</strong> {category} | 
                    <strong>Difficulty:</strong> {difficulty}</p>
            """, unsafe_allow_html=True)

            # Display context if available
            if context:
                st.markdown("**Context:**")
                st.markdown(f"*{context}*")

            # Display question
            st.write(f"**{question_text}**")

            # Handle options and user selection
            if isinstance(options, dict) and options:
                formatted_options = [f"{k}: {v}" for k, v in options.items()]
                answer_key = f"answer_{index}"
                choice = st.radio("Select your answer:", formatted_options, key=answer_key)
                selected_letter = choice[0] if choice else None

                # Submit button
                if st.button("Submit Answer", key=f"submit_{index}"):
                    correct_answer = question.get('correct_option')
                    if selected_letter == correct_answer:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is {correct_answer}")
                    st.info(f"**Explanation:** {question.get('explanation', 'No explanation provided.')}")
            else:
                st.error("Invalid question format")

            # Close the div after all content is added
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
        st.write("Raw question data:", question)


def display_questions_grid(questions: List[Dict]) -> None:
    """Display questions in a 2-column grid layout"""
    # Add CSS for better spacing
    st.markdown("""
        <style>
            [data-testid="column"] {
                padding: 0 1rem;
            }
            div.stButton > button {
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)

    num_questions = len(questions)
    num_rows = ceil(num_questions / 2)

    for row in range(num_rows):
        col1, col2 = st.columns(2)

        first_idx = row * 2
        if first_idx < num_questions:
            with col1:
                display_question_card(questions[first_idx], first_idx, col1)

        second_idx = row * 2 + 1
        if second_idx < num_questions:
            with col2:
                display_question_card(questions[second_idx], second_idx, col2)


def generate_questions(personal_data: Dict, regional_data: Dict) -> Optional[List[Dict]]:
    """Make API call to generate questions"""
    try:
        response = requests.post(
            "http://localhost:5000/generate-questions",
            json={
                "user_results": personal_data,
                "regional_results": regional_data
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json().get('questions', [])
        else:
            st.error(f"API Error: {response.json().get('message', 'Unknown error')}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend server. Please make sure it's running.")
        return None
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return None


def show_analytics():
    """Display the analytics page."""
    st.title("Analytics Dashboard")
    st.write("This is where you can view analytics related to your practice questions.")

    # Add more analytics-related content here


def main():
    """Main application logic."""
    st.set_page_config(page_title="ACT Practice Questions", layout="wide")

    # Custom CSS for the page
    st.markdown("""
        <style>
            div.stButton > button {
                width: 100%;
            }
            .stSuccess, .stError, .stInfo {
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2 = st.columns([4, 1])  # Adjust column sizes as needed

    with col1:
        st.title("ACT Practice Question Generator")

    with col2:
        if st.button("View Analytics"):
            st.session_state.current_page = 'analytics'  # Change current page to analytics

    # Page navigation logic
    if st.session_state.current_page == 'main':
        # Create two columns for scores
        col1, col2 = st.columns(2)

        with col1:
            st.header("Regional Scores")
            regional_data = {
                "Mathematics": st.slider("Math", 0, 36, 18, key="r_math"),
                "Reading": st.slider("Reading", 0, 36, 18, key="r_reading"),
                "Science": st.slider("Science", 0, 36, 18, key="r_science"),
                "English": st.slider("English", 0, 36, 18, key="r_english")
            }

        with col2:
            st.header("Your Scores")
            personal_data = {
                "Mathematics": st.slider("Math", 0, 36, 13, key="p_math"),
                "Reading": st.slider("Reading", 0, 36, 13, key="p_reading"),
                "Science": st.slider("Science", 0, 36, 13, key="p_science"),
                "English": st.slider("English", 0, 36, 13, key="p_english")
            }

        # Generate questions button
        st.markdown("---")
        if st.button("Generate Questions", type="primary", use_container_width=True):
            with st.spinner("Generating questions..."):
                questions = generate_questions(personal_data, regional_data)
                if questions:
                    st.session_state.questions = questions
                    st.success("Questions generated successfully!")

        # Display questions if they exist
        if st.session_state.questions:
            st.markdown("## Practice Questions")
            display_questions_grid(st.session_state.questions)

            if st.button("Reset All Answers", use_container_width=True):
                # Clear answers from session state
                for key in list(st.session_state.keys()):
                    if key.startswith("answer_"):
                        del st.session_state[key]

                del st.session_state.questions

                # Refresh page to reflect changes.
          ## st.experimental_rerun()

        # Backend status in sidebar
    try:
        health_response = requests.get("http://localhost:5000/health")
        if health_response.status_code == 200:
            st.sidebar.success("Backend: Connected")
        else:
            st.sidebar.error("Backend: Error")
    except Exception as e:
        print(e)
        st.sidebar.error("Backend: Not Connected")


if __name__ == "__main__":
    main()