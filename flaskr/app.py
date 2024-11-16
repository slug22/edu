from flask import Flask, request, jsonify, render_template_string
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# For testing purposes - hardcoded API key (remember to remove in production!)
SAMBANOVA_API_KEY = "cf134cde-f4d2-4e6d-90b4-500e269eb286" # Replace with your actual test API key

app = Flask(__name__)

# Configure OpenAI client for SambaNova
client = openai.OpenAI(
    api_key=SAMBANOVA_API_KEY,  # Using hardcoded key for testing
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


def generate_questions(user_results, regional_results):
    """
    Generate questions based on test results using LLaMA API
    """
    prompt = f"""
    Given the following test results:
    User ACT Results: {user_results}
    Regional ACT Results: {regional_results}
    USA Median ACT Results: {SAMPLE_USA_RESULTS}
    
    Generate 5 relevant practice questions that focus on areas where improvement is needed,
    comparing individual performance against regional averages.
    """
    
    try:
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": "You are an educational assistant that generates targeted practice questions based on weaknesses and test performance analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

# HTML template for the test interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Question Generator Test Interface</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 20px; }
        textarea { width: 100%; height: 150px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>Question Generator Test Interface</h1>
    
    <div class="form-group">
        <h3>Use Sample Data</h3>
        <form action="/test-sample" method="post">
            <button type="submit">Generate Questions with Sample Data</button>
        </form>
    </div>

    <div class="form-group">
        <h3>Custom Data</h3>
        <form action="/test-custom" method="post">
            <label>User Results (JSON):</label><br>
            <textarea name="user_results">{"English": 21,
"Mathematics": 21,
"Reading": 21,
"Science": 21}</textarea><br><br>
            
            <label>Regional Results (JSON):</label><br>
            <textarea name="regional_results">{"English": 21,
"Mathematics": 21,
"Reading": 21,
"Science": 21}</textarea><br><br>
            
            <button type="submit">Generate Questions</button>
        </form>
    </div>

    {% if result %}
    <div class="result">
        <h3>Generated Questions:</h3>
        <pre>{{ result }}</pre>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def test_interface():
    """
    Test interface endpoint
    """
    return render_template_string(HTML_TEMPLATE)

@app.route('/test-sample', methods=['POST'])
def test_with_sample():
    """
    Test endpoint using sample data
    """
    questions = generate_questions(SAMPLE_USER_RESULTS, SAMPLE_REGIONAL_RESULTS)
    print(questions)
    return render_template_string(HTML_TEMPLATE, result=questions)

@app.route('/test-custom', methods=['POST'])
def test_with_custom():
    """
    Test endpoint using custom data
    """
    try:
        user_results = eval(request.form['user_results'])
        regional_results = eval(request.form['regional_results'])
        questions = generate_questions(user_results, regional_results)
        return render_template_string(HTML_TEMPLATE, result=questions)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, result=f"Error: {str(e)}")

@app.route('/generate-questions', methods=['POST'])
def create_questions():
    """
    API endpoint to generate questions
    """
    try:
        data = request.get_json()
        
        # Validate input
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
        print(questions)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)