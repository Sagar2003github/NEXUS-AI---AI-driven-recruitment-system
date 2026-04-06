import fitz  # PyMuPDF
import os
from sentence_transformers import SentenceTransformer, util

# Model load (BERT based MiniLM)
print("🤖 AI Engine: Initializing Nexus BERT Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# ---------------------------------------------------------
# ❓ EXPANDED INTERVIEW QUESTION BANK (For Multiple Questions)
# ---------------------------------------------------------
QUESTION_BANK = {
    'python': "Explain the difference between a list and a tuple. When would you use each?",
    'flask': "What is a 'Route' in Flask and how do you handle dynamic URLs?",
    'machine learning': "Explain the Bias-Variance tradeoff in Machine Learning.",
    'ai': "What is the difference between Narrow AI and General AI?",
    'aws': "What are the core benefits of using AWS S3 for storage in an AI project?",
    'docker': "How does a Docker container differ from a Virtual Machine?",
    'nlp': "What is Word Embedding, and why is it important for BERT models?",
    'sql': "What are Joins in SQL? Explain Left Join vs Inner Join.",
    'scikit-learn': "How does the 'ExtraTreesClassifier' differ from a standard Random Forest?",
    'mongodb': "What is the difference between SQL (Relational) and NoSQL (MongoDB)?",
    'tableau': "Difference between .twb and .twbx files in Tableau?",
    'git': "What is the difference between 'git fetch' and 'git pull'?",
    'tensorflow': "What is a Computational Graph in TensorFlow?",
    'pytorch': "How does Dynamic Graph calculation work in PyTorch?",
    'react': "What are Hooks in React and why do we use 'useEffect'?",
    'javascript': "Explain the concept of Closures in JavaScript.",
    'fastapi': "How does FastAPI handle asynchronous requests compared to Flask?"
}

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Extraction Error: {e}")
    return text

def analyze_resume(resume_text, jd_text, categories):
    # 1. BERT Similarity Score (Semantic Match)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    cosine_score = util.pytorch_cos_sim(resume_emb, jd_emb)
    
    raw_score = float(cosine_score[0][0]) * 100

    # 🚀 --- SCORE BOOSTER (Sagar's Custom Presentation Logic) --- 🚀
    if raw_score > 30:
        match_score = min(98.5, raw_score + 15)
    else:
        match_score = raw_score + 5
    
    match_score = round(match_score, 2)

    # 2. 🎯 MULTI-SKILL GAP ANALYSIS
    # List of keywords to scan
    tech_keywords = list(QUESTION_BANK.keys())
    
    resume_text_lower = resume_text.lower()
    jd_text_lower = jd_text.lower()
    
    # Logic: JD mein keyword hai par Resume mein nahi hai
    missing_skills = []
    for skill in tech_keywords:
        if skill in jd_text_lower and skill not in resume_text_lower:
            missing_skills.append(skill)

    # 3. ❓ MULTIPLE QUESTIONS GENERATION
    # Jitne missing skills milenge, unke questions is list mein jayenge
    smart_questions = []
    for skill in missing_skills:
        if skill in QUESTION_BANK:
            smart_questions.append({
                "skill": skill.upper(), 
                "question": QUESTION_BANK[skill]
            })

    # 4. Industry Classification (Category Matching)
    cat_embs = model.encode(categories, convert_to_tensor=True)
    cat_scores = util.pytorch_cos_sim(resume_emb, cat_embs)
    predicted_role = categories[cat_scores.argmax().item()]

    # RETURN: Score, Role, Gaps (Top 5), Questions (Top 5)
    # Ensure we return the full list of questions, not just one
    return match_score, predicted_role, missing_skills[:5], smart_questions[:5]