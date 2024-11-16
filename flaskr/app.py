from flask import Flask, request, jsonify, render_template_string
import os
import openai
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI client for SambaNova
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY", "cf134cde-f4d2-4e6d-90b4-500e269eb286")
client = openai.OpenAI(
    api_key=SAMBANOVA_API_KEY,
    base_url="https://api.sambanova.ai/v1"
)

# Sample test data
SAMPLE_USER_RESULTS = {
    "English": 20,
    "Mathematics": 11,
    "Reading": 11,
    "Science": 19
}

SAMPLE_REGIONAL_RESULTS = {
    "English": 15,
    "Mathematics": 15,
    "Reading": 15,
    "Science": 15
}

SAMPLE_USA_RESULTS = {
    "English": 21,
    "Mathematics": 21,
    "Reading": 21,
    "Science": 21
}
# Add this HTML_TEMPLATE constant right after the sample data constants and before the functions

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ACT Question Generator</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1000px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .form-group { 
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        textarea { 
            width: 100%; 
            height: 150px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: monospace;
            margin-top: 5px;
        }
        button { 
            padding: 10px 20px; 
            background-color: #4CAF50; 
            color: white; 
            border: none; 
            cursor: pointer;
            border-radius: 4px;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        .result { 
            margin-top: 20px; 
            white-space: pre-wrap;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h3 {
            color: #333;
        }
        label {
            font-weight: bold;
            color: #555;
        }
        pre {
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .info {
            margin-bottom: 10px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>ACT Question Generator</h1>
    
    <div class="form-group">
        <h3>Generate with Sample Data</h3>
        <div class="info">Test the generator with predefined sample scores</div>
        <form action="/test-sample" method="post">
            <button type="submit">Generate Sample Questions</button>
        </form>
    </div>

    <div class="form-group">
        <h3>Custom Test Data</h3>
        <div class="info">Enter custom ACT scores to generate targeted practice questions</div>
        <form action="/test-custom" method="post">
            <label>User Results (JSON):</label><br>
            <textarea name="user_results">{
    "English": 21,
    "Mathematics": 21,
    "Reading": 21,
    "Science": 21
}</textarea><br><br>
            
            <label>Regional Results (JSON):</label><br>
            <textarea name="regional_results">{
    "English": 21,
    "Mathematics": 21,
    "Reading": 21,
    "Science": 21
}</textarea><br><br>
            
            <button type="submit">Generate Custom Questions</button>
        </form>
    </div>

    {% if result %}
    <div class="result">
        <h3>Generated Questions:</h3>
        <pre>{{ result }}</pre>
    </div>
    {% endif %}

    {% if error %}
    <div class="error">
        {{ error }}
    </div>
    {% endif %}
</body>
</html>
"""
def generate_questions(user_results: Dict, regional_results: Dict) -> List[Dict]:
    """
    Generate and parse ACT practice questions based on test results using LLaMA API
    """
    prompt = f"""
    Given the following test results:
    User ACT Results: {user_results}
    Regional ACT Results: {regional_results}
    USA Median ACT Results: {SAMPLE_USA_RESULTS}
    
    Generate 5 ACT-style multiple choice practice questions focusing on areas needing improvement.
    For each question, provide:
    1. The question text
    2. Four multiple choice options (A, B, C, D)
    3. The correct answer (indicate which letter is correct)
    4. A brief explanation of why the answer is correct
    5. The category (Reading/Math/Science/English)
    6. Difficulty level (Easy/Medium/Hard)
    
    Format each question as JSON with the following structure:
    {{
        "question": "question text",
        "options": {{
            "A": "first option",
            "B": "second option",
            "C": "third option",
            "D": "fourth option"
        }},
        "correct_option": "A",
        "explanation": "explanation text",
        "category": "subject category",
        "difficulty": "difficulty level"
    }}
    
    Return all questions in a JSON array. Make sure distractors (incorrect options) are plausible 
    but clearly incorrect to a knowledgeable test-taker. Include common misconceptions as distractors.
    The correct answer should be randomly distributed among A, B, C, and D across questions.
    """
    
    try:
        logger.debug(f"Sending request to API with user_results: {user_results}")
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assistant that generates targeted practice questions based on weaknesses and test performance analysis. Return responses in JSON format."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the actual response content
        response_content = response.choices[0].message.content
        logger.debug(f"Raw response content: {response_content}")
        
        # Clean up the response content - remove markdown code blocks if present
        cleaned_content = response_content
        if "```json" in cleaned_content:
            cleaned_content = cleaned_content.split("```json")[1]
        if "```" in cleaned_content:
            cleaned_content = cleaned_content.split("```")[0]
        
        cleaned_content = cleaned_content.strip()
        logger.debug(f"Cleaned content: {cleaned_content}")
        
        # Parse the response into structured format
        try:
            questions = json.loads(cleaned_content)
            logger.debug(f"Parsed JSON questions: {questions}")
            
            # Validate the structure of each question
            validated_questions = []
            required_fields = {"question", "options", "correct_option", "explanation", "category", "difficulty"}
            
            for q in questions:
                if all(field in q for field in required_fields):
                    if isinstance(q["options"], dict) and all(opt in q["options"] for opt in ["A", "B", "C", "D"]):
                        validated_questions.append(q)
                    else:
                        logger.warning(f"Invalid options format in question: {q}")
                else:
                    logger.warning(f"Skipping invalid question format: {q}")
            
            if not validated_questions:
                logger.info("No valid questions found, attempting unstructured parsing")
                return parse_unstructured_response(cleaned_content)
            
            return validated_questions
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            logger.info("Attempting unstructured response parsing")
            return parse_unstructured_response(cleaned_content)
            
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        return [{"error": str(e), "question": "Error generating question", 
                "options": {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"},
                "correct_option": "A",
                "explanation": str(e), "category": "Error", "difficulty": "N/A"}]

def parse_unstructured_response(response_text: str) -> List[Dict]:
    """
    Enhanced fallback parser for unstructured text responses
    """
    logger.debug(f"Parsing unstructured response: {response_text}")
    questions = []
    current_question = {}
    current_options = {}
    
    lines = response_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        logger.debug(f"Processing line: {line}")
        
        if any(line.lower().startswith(start) for start in ['q:', 'question:', 'problem:']):
            if current_question and current_question.get('question'):
                current_question['options'] = current_options
                questions.append(current_question)
            current_question = {
                "question": line.split(':', 1)[1].strip(),
                "options": {},
                "correct_option": "A",
                "explanation": "",
                "category": "Unknown",
                "difficulty": "Medium"
            }
            current_options = {}
        elif line.startswith('A)') or line.startswith('A.'):
            current_options["A"] = line.split(')', 1)[1].strip() if ')' in line else line.split('.', 1)[1].strip()
        elif line.startswith('B)') or line.startswith('B.'):
            current_options["B"] = line.split(')', 1)[1].strip() if ')' in line else line.split('.', 1)[1].strip()
        elif line.startswith('C)') or line.startswith('C.'):
            current_options["C"] = line.split(')', 1)[1].strip() if ')' in line else line.split('.', 1)[1].strip()
        elif line.startswith('D)') or line.startswith('D.'):
            current_options["D"] = line.split(')', 1)[1].strip() if ')' in line else line.split('.', 1)[1].strip()
        elif line.lower().startswith('correct:') or line.lower().startswith('answer:'):
            answer_text = line.split(':', 1)[1].strip()
            if answer_text.upper() in ['A', 'B', 'C', 'D']:
                current_question["correct_option"] = answer_text.upper()
        elif line.lower().startswith('explanation:'):
            current_question["explanation"] = line.split(':', 1)[1].strip()
        elif line.lower().startswith('category:'):
            current_question["category"] = line.split(':', 1)[1].strip()
        elif line.lower().startswith('difficulty:'):
            current_question["difficulty"] = line.split(':', 1)[1].strip()
    
    # Add the last question if exists
    if current_question and current_question.get('question'):
        current_question['options'] = current_options
        questions.append(current_question)
    
    logger.debug(f"Parsed questions: {questions}")
    return questions if questions else [{"question": "Failed to generate questions", 
                                      "options": {"A": "N/A", "B": "N/A", "C": "N/A", "D": "N/A"},
                                      "correct_option": "A",
                                      "explanation": "The API response format was unexpected", 
                                      "category": "Error", "difficulty": "N/A"}]
@app.route('/')
def test_interface():
    """Test interface endpoint"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/test-sample', methods=['POST'])
def test_with_sample():
    """Test endpoint using sample data"""
    try:
        logger.info("Generating questions with sample data")
        questions = generate_questions(SAMPLE_USER_RESULTS, SAMPLE_REGIONAL_RESULTS)
        logger.debug(f"Generated questions: {questions}")
        # Properly format the result as JSON string
        result = json.dumps(questions, indent=2)
        return render_template_string(HTML_TEMPLATE, result=result)
    except Exception as e:
        logger.error(f"Error in test_with_sample: {e}")
        error_response = [{"error": str(e), "question": "Error occurred", "answer": "N/A",
                          "explanation": str(e), "category": "Error", "difficulty": "N/A"}]
        return render_template_string(HTML_TEMPLATE, result=json.dumps(error_response, indent=2))

@app.route('/test-custom', methods=['POST'])
def test_with_custom():
    """Test endpoint using custom data"""
    try:
        # Safely parse JSON instead of using eval
        user_results = json.loads(request.form['user_results'])
        regional_results = json.loads(request.form['regional_results'])
        questions = generate_questions(user_results, regional_results)
        return render_template_string(HTML_TEMPLATE, result=json.dumps(questions, indent=2))
    except Exception as e:
        logger.error(f"Error in test_with_custom: {e}")
        error_response = [{"error": str(e), "question": "Error occurred", "answer": "N/A",
                          "explanation": str(e), "category": "Error", "difficulty": "N/A"}]
        return render_template_string(HTML_TEMPLATE, result=json.dumps(error_response, indent=2))

@app.route('/generate-questions', methods=['POST'])
def create_questions():
    """API endpoint to generate questions"""
    try:
        data = request.get_json()
        
        if not data or 'user_results' not in data or 'regional_results' not in data:
            return jsonify({
                'error': 'Missing required fields. Please provide user_results and regional_results.'
            }), 400
            
        questions = generate_questions(
            data['user_results'],
            data['regional_results']
        )
        
        return jsonify({
            'status': 'success',
            'questions': questions
        })
    except Exception as e:
        logger.error(f"Error in create_questions: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)