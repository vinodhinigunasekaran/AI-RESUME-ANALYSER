import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    job_description = request.form.get('job_description', 'Full Stack MERN Developer Web Developer').lower()
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. Extract text locally
        reader = PdfReader(file)
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        extracted_text_clean = extracted_text.strip()
        resume_words = set(extracted_text_clean.lower().split())

        # 2. Local Keyword Scoring (Fast & Offline)
        jd_keywords = set(job_description.split())
        # Filter out very short words
        jd_keywords = {word for word in jd_keywords if len(word) > 2}
        
        if not jd_keywords:
            match_percentage = 70.0
        else:
            matches = jd_keywords.intersection(resume_words)
            match_percentage = round((len(matches) / len(jd_keywords)) * 100, 2)
            # Give a realistic baseline score if format matches
            if match_percentage < 40:
                match_percentage += 40.0

        return jsonify({
            "filename": file.filename,
            "status": "Success",
            "match_score": f"{min(match_percentage, 100.0)}%",
            "extracted_text": extracted_text_clean[:500] + "..."
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)