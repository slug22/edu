import streamlit as st
import requests
import json


def main():
    st.set_page_config(
        page_title="Data Entry and Question Generator",
        page_icon="📝",
        layout="wide"
    )

    st.title("Data Entry and Question Generator 📝")

    # Create two columns for the two sections
    col1, col2 = st.columns(2)

    # Initialize session state for storing questions
    if 'questions' not in st.session_state:
        st.session_state.questions = None

    with col1:
        st.header("Regional Data")
        st.markdown("---")

        # Regional data fields with sliders
        regional_data = {
            "math": st.slider(
                "Math Score (Regional)",
                min_value=0,
                max_value=36,
                value=18,
                key="r_math",
                help="Regional average math score"
            ),
            "reading": st.slider(
                "Reading Score (Regional)",
                min_value=0,
                max_value=36,
                value=18,
                key="r_reading",
                help="Regional average reading score"
            ),
            "science": st.slider(
                "Science Score (Regional)",
                min_value=0,
                max_value=36,
                value=18,
                key="r_science",
                help="Regional average science score"
            ),
            "english": st.slider(
                "English Score (Regional)",
                min_value=0,
                max_value=36,
                value=18,
                key="r_english",
                help="Regional average english score"
            )
        }

        # Display the selected regional values
        st.markdown("### Selected Regional Scores:")
        for subject, score in regional_data.items():
            st.write(f"**{subject.title()}:** {score}")

    with col2:
        st.header("Personal Data")
        st.markdown("---")

        # Personal data fields with sliders
        personal_data = {
            "math": st.slider(
                "Math Score (Personal)",
                min_value=0,
                max_value=36,
                value=13,
                key="p_math",
                help="Drag to set personal math score"
            ),
            "reading": st.slider(
                "Reading Score (Personal)",
                min_value=0,
                max_value=36,
                value=13,
                key="p_reading",
                help="Drag to set personal reading score"
            ),
            "science": st.slider(
                "Science Score (Personal)",
                min_value=0,
                max_value=36,
                value=13,
                key="p_science",
                help="Drag to set personal science score"
            ),
            "english": st.slider(
                "English Score (Personal)",
                min_value=0,
                max_value=36,
                value=13,
                key="p_english",
                help="Drag to set personal english score"
            )
        }

        # Display the selected personal values
        st.markdown("### Selected Personal Scores:")
        for subject, score in personal_data.items():
            st.write(f"**{subject.title()}:** {score}")

    # Submit button centered at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("Generate Questions", use_container_width=True, type="primary"):
            try:
                # Prepare the data for the API request
                data = {
                    "user_results": personal_data,
                    "regional_results": regional_data  # Fixed: using regional_data instead of undefined region_data
                }

                # Make POST request to Flask backend
                response = requests.post(
                    "http://localhost:5000/generate-questions",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.questions = result['questions']
                    st.success("Questions generated successfully!")
                else:
                    st.error(f"Error: {response.json().get('message', 'Unknown error occurred')}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server. Please make sure it's running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display generated questions if they exist
    if st.session_state.questions:
        st.markdown("### Generated Practice Questions:")
        st.markdown(st.session_state.questions)

    # Add a button to use sample data
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Use Sample Data", use_container_width=True):
            try:
                response = requests.post("http://localhost:5000/test-sample")
                if response.status_code == 200:
                    st.session_state.questions = response.json().get('questions', 'No questions generated')
                    st.success("Sample questions generated successfully!")
                else:
                    st.error("Error generating sample questions")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server. Please make sure it's running.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Add health check indicator
    try:
        health_response = requests.get("http://localhost:5000/health")
        if health_response.status_code == 200:
            st.sidebar.success("Backend Status: Connected")
        else:
            st.sidebar.error("Backend Status: Error")
    except:
        st.sidebar.error("Backend Status: Not Connected")


if __name__ == "__main__":
    main()
