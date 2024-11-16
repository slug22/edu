import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

class EducationAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def generate_questions(self, user_results, regional_results):
        response = requests.post(
            f"{self.base_url}/generate-questions",
            json={
                "user_results": user_results,
                "regional_results": regional_results
            }
        )
        return response.json()

    def submit_answer(self, question, answer):
        response = requests.post(
            f"{self.base_url}/submit-answer",
            json={
                "question": question,
                "answer": answer
            }
        )
        return response.json()

    def get_history(self, limit=50):
        response = requests.get(
            f"{self.base_url}/question-history",
            params={"limit": limit}
        )
        return response.json()

def main():
    st.set_page_config(
        page_title="Educational Practice Platform",
        page_icon="📚",
        layout="wide"
    )

    # Initialize API client
    api = EducationAPI()

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Generate Questions", "Practice Questions", "Performance Analytics"]
    )

    if page == "Generate Questions":
        show_question_generator(api)
    elif page == "Practice Questions":
        show_practice_interface(api)
    else:
        show_analytics(api)

def show_question_generator(api):
    st.title("📝 Question Generator")
    
    # Input for test results
    st.subheader("Enter Test Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Your Results")
        math_score = st.slider("Math Score", 0, 100, 75, key="user_math")
        science_score = st.slider("Science Score", 0, 100, 80, key="user_science")
        user_results = {
            "math": math_score,
            "science": science_score
        }

    with col2:
        st.markdown("### Regional Results")
        regional_math = st.slider("Regional Math Average", 0, 100, 85, key="regional_math")
        regional_science = st.slider("Regional Science Average", 0, 100, 82, key="regional_science")
        regional_results = {
            "math": regional_math,
            "science": regional_science
        }

    if st.button("Generate Practice Questions"):
        with st.spinner("Generating questions..."):
            try:
                response = api.generate_questions(user_results, regional_results)
                if response["status"] == "success":
                    st.session_state.questions = response["questions"]
                    st.success(f"Generated {len(response['questions'])} questions!")
                    
                    # Display metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Topics Covered")
                        for topic in response["metadata"]["topics_covered"]:
                            st.write(f"- {topic}")
                    
                    with col2:
                        st.markdown("### Difficulty Distribution")
                        dist = response["metadata"]["difficulty_distribution"]
                        fig = px.pie(
                            values=list(dist.values()),
                            names=list(dist.keys()),
                            title="Question Difficulty Distribution"
                        )
                        st.plotly_chart(fig)
                else:
                    st.error("Failed to generate questions")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_practice_interface(api):
    st.title("✍️ Practice Questions")
    
    if "questions" not in st.session_state:
        st.warning("Please generate questions first!")
        return
    
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    
    if "answers" not in st.session_state:
        st.session_state.answers = []
    
    questions = st.session_state.questions
    current_q = st.session_state.current_question
    
    # Display progress
    progress = (current_q + 1) / len(questions)
    st.progress(progress)
    st.write(f"Question {current_q + 1} of {len(questions)}")
    
    # Display current question
    question = questions[current_q]
    st.markdown(f"### {question['question']}")
    st.markdown(f"**Topic:** {question['topic']} - **Difficulty:** {question['difficulty'].title()}")
    
    # Display options and get answer
    answer = st.radio(
        "Select your answer:",
        [opt.split(") ")[1] for opt in question["options"]],
        key=f"q_{current_q}"
    )
    
    # Submit answer
    if st.button("Submit Answer"):
        try:
            response = api.submit_answer(
                question,
                chr(65 + [opt.split(") ")[1] for opt in question["options"]].index(answer))
            )
            
            if response["status"] == "success":
                if response["is_correct"]:
                    st.success("Correct! 🎉")
                else:
                    st.error("Incorrect. Try again! 📚")
                
                st.info(f"Explanation: {response['explanation']}")
                
                # Store answer
                st.session_state.answers.append({
                    "question": current_q + 1,
                    "correct": response["is_correct"]
                })
                
                # Move to next question
                if current_q < len(questions) - 1:
                    st.session_state.current_question += 1
                    st.experimental_rerun()
                else:
                    st.balloons()
                    st.success("You've completed all questions!")
        except Exception as e:
            st.error(f"Error submitting answer: {str(e)}")

def show_analytics(api):
    st.title("📊 Performance Analytics")
    
    try:
        response = api.get_history()
        if response["status"] == "success":
            history = response["history"]
            
            # Convert history to DataFrame
            df = pd.DataFrame(history)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Overall statistics
            st.subheader("Overall Performance")
            total = len(history)
            correct = response["metadata"]["correct_count"]
            accuracy = (correct / total * 100) if total > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Questions", total)
            col2.metric("Correct Answers", correct)
            col3.metric("Accuracy", f"{accuracy:.1f}%")
            
            # Performance over time
            st.subheader("Performance Over Time")
            df['date'] = df['timestamp'].dt.date
            daily_performance = df.groupby('date')['is_correct'].agg(['count', 'mean'])
            daily_performance.columns = ['Questions Attempted', 'Accuracy']
            
            fig = px.line(
                daily_performance,
                y='Accuracy',
                title='Daily Accuracy Trend'
            )
            st.plotly_chart(fig)
            
            # Topic analysis
            st.subheader("Topic Performance")
            topic_performance = df.groupby(df['question'].apply(lambda x: x['topic']))['is_correct'].agg(['count', 'mean'])
            topic_performance.columns = ['Questions Attempted', 'Accuracy']
            
            fig = px.bar(
                topic_performance,
                y='Accuracy',
                title='Accuracy by Topic'
            )
            st.plotly_chart(fig)
            
        else:
            st.error("Failed to fetch history")
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

if __name__ == "__main__":
    main()