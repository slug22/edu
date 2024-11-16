import streamlit as st
import requests
import json
from typing import Dict, List, Optional

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = None

def display_question_card(question: Dict, index: int) -> None:
    """Display an individual question card with interactive elements"""
    try:
        st.subheader(f"Question {index + 1}")
        st.write(f"**Category:** {question.get('category', 'Unknown')} | **Difficulty:** {question.get('difficulty', 'Unknown')}")
        
        # Display context if available
        context = question.get('context', '').strip()
        if context:
            st.markdown("**Context:**")
            st.markdown(f"*{context}*")
            st.markdown("---")
        
        # Question text
        st.write(f"**{question.get('question', '')}**")
        
        # Create a unique key for this question's state
        answer_key = f"answer_{index}"
        
        # Get options and create radio
        options = question.get('options', {})
        if isinstance(options, dict) and options:
            # Format options for display
            formatted_options = [f"{k}: {v}" for k, v in options.items()]
            
            # Radio button for answer selection
            choice = st.radio(
                "Select your answer:",
                formatted_options,
                key=answer_key,
            )
            
            # Extract selected letter (first character of the selection)
            selected_letter = choice[0] if choice else None
            
            # Check answer button
            if st.button("Submit Answer", key=f"submit_{index}"):
                correct_answer = question.get('correct_option')
                if selected_letter == correct_answer:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is {correct_answer}")
                st.info(f"**Explanation:** {question.get('explanation', 'No explanation provided.')}")
        else:
            st.error("Invalid question format")
            
    except Exception as e:
        st.error(f"Error displaying question: {str(e)}")
        st.write("Raw question data:", question)
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

def main():
    st.set_page_config(page_title="ACT Practice Questions", layout="wide")
    st.title("ACT Practice Question Generator")

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
        for i, question in enumerate(st.session_state.questions):
            with st.container():
                st.markdown("---")
                display_question_card(question, i)

        if st.button("Reset All Answers"):
            # Clear answers from session state
            for key in list(st.session_state.keys()):
                if key.startswith("answer_"):
                    del st.session_state[key]
            st.experimental_rerun()

    # Backend status in sidebar
    try:
        health_response = requests.get("http://localhost:5000/health")
        if health_response.status_code == 200:
            st.sidebar.success("Backend: Connected")
        else:
            st.sidebar.error("Backend: Error")
    except:
        st.sidebar.error("Backend: Not Connected")

if __name__ == "__main__":
    main()