"""
Google Gemini AI Service for resume analysis.
Falls back to intelligent mock data if no API key is configured.
"""
import json
import os
import re


def _mock_analysis(resume_text):
    """Return realistic mock analysis data for development."""
    word_count = len(resume_text.split())
    ats_score = min(95, max(45, 60 + (word_count // 50)))
    resume_score = min(90, max(40, ats_score - 5))

    return {
        "ats_score": ats_score,
        "resume_score": resume_score,
        "summary": (
            "This resume demonstrates a solid professional background with relevant experience. "
            "The candidate shows strong technical skills and has structured their resume well. "
            "Some improvements can be made to better optimize for ATS systems and highlight key achievements."
        ),
        "strengths": [
            "Clear and organized structure with logical sections",
            "Relevant technical skills listed prominently",
            "Professional experience section is detailed",
            "Educational qualifications are clearly presented",
            "Contact information is complete and professional",
        ],
        "weaknesses": [
            "Professional summary could be more impactful",
            "Achievement metrics (numbers/percentages) are missing",
            "Some bullet points are too vague or generic",
            "Keywords from target job roles could be better integrated",
            "Projects section could benefit from more technical details",
        ],
        "grammar_suggestions": [
            "Use active voice consistently throughout (e.g., 'Led team' instead of 'Was responsible for leading')",
            "Maintain consistent verb tense in experience descriptions",
            "Avoid starting multiple bullet points with the same word",
            "Check for proper capitalization of technical terms and tools",
        ],
        "formatting_suggestions": [
            "Ensure consistent font sizes across all section headings",
            "Add more white space between sections for better readability",
            "Use bullet points consistently — avoid mixing bullets and paragraphs",
            "Keep resume to 1-2 pages maximum",
            "Align dates to the right margin for a cleaner look",
        ],
        "missing_skills": [
            "Docker / Containerization",
            "CI/CD Pipeline (GitHub Actions, Jenkins)",
            "Cloud platforms (AWS / Azure / GCP)",
            "Unit Testing / Test-Driven Development",
            "Agile / Scrum methodology",
        ],
        "missing_keywords": [
            "scalable", "cross-functional", "stakeholder management",
            "data-driven", "optimization", "deployment", "architecture",
        ],
        "ai_recommendations": [
            "Add a compelling 3-4 line professional summary at the top highlighting your unique value",
            "Quantify achievements: replace 'improved performance' with 'improved performance by 35%'",
            "Tailor your skills section to match keywords from the job description",
            "Add a Projects section with links to GitHub repositories if available",
            "Include certifications from platforms like Coursera, AWS, or Google to boost credibility",
            "Use industry-standard action verbs: Developed, Architected, Optimized, Deployed, Integrated",
            "Add LinkedIn and GitHub profile links to your contact information",
        ]
    }


def _mock_jd_match(resume_text, job_description):
    """Return realistic mock job description match data."""
    jd_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())
    common = jd_words & resume_words
    match_pct = min(85, max(30, int(len(common) / max(len(jd_words), 1) * 100) + 20))

    return {
        "match_percentage": match_pct,
        "matching_skills": [
            "Python", "Django", "REST API", "SQL", "Git", "Problem Solving"
        ],
        "missing_skills": [
            "Kubernetes", "Microservices", "Redis", "Elasticsearch", "GraphQL"
        ],
        "keyword_match": [
            "experience", "development", "team", "project", "technology", "solution"
        ],
        "improvement_suggestions": [
            "Add specific keywords from the job description to your skills section",
            "Mention experience with the tech stack listed in the JD",
            "Highlight any leadership or team collaboration experience",
            "Include metrics that align with the job's KPIs",
            "Tailor your professional summary specifically for this role",
        ]
    }


def _mock_improvement(section, content):
    """Return mock improvement suggestions."""
    improvements = {
        "summary": {
            "improved": (
                "Results-driven Software Developer with 3+ years of experience designing and building "
                "scalable web applications using Python, Django, and modern cloud technologies. "
                "Proven track record of delivering high-quality solutions that improve operational efficiency "
                "by 30%+. Passionate about clean code, agile practices, and continuous learning."
            ),
            "tips": [
                "Lead with your years of experience",
                "Mention 2-3 core technologies",
                "Include a quantifiable achievement",
                "End with your career passion or goal"
            ]
        },
        "experience": {
            "improved": (
                "• Architected and deployed a microservices-based e-commerce platform serving 50K+ daily users\n"
                "• Reduced API response time by 40% through database query optimization and Redis caching\n"
                "• Led a cross-functional team of 5 developers in delivering 3 major product releases on schedule\n"
                "• Implemented automated CI/CD pipeline reducing deployment time from 2 hours to 15 minutes"
            ),
            "tips": [
                "Start each bullet with a strong action verb",
                "Include specific metrics and percentages",
                "Mention team size and scope of projects",
                "Highlight technologies used"
            ]
        },
        "skills": {
            "improved": (
                "Programming Languages: Python, JavaScript, SQL, Java\n"
                "Frameworks & Libraries: Django, FastAPI, React, NumPy, Pandas\n"
                "Databases: PostgreSQL, MySQL, MongoDB, Redis\n"
                "DevOps & Cloud: Docker, AWS (EC2, S3, RDS), GitHub Actions, Nginx\n"
                "Tools: Git, VS Code, Postman, Jira, Figma"
            ),
            "tips": [
                "Group skills by category",
                "List most relevant skills first",
                "Include proficiency levels if appropriate",
                "Add tools and platforms, not just languages"
            ]
        }
    }
    return improvements.get(section, improvements["summary"])


def analyze_resume(resume_text):
    """
    Analyze a resume using Gemini AI.
    Falls back to mock data if API key is not configured.
    """
    api_key = os.getenv('GEMINI_API_KEY', '')

    if not api_key or api_key == 'your-gemini-api-key-here':
        return _mock_analysis(resume_text)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
You are an expert resume analyst and career coach. Analyze the following resume and provide a comprehensive evaluation.

Return ONLY a valid JSON object with exactly this structure (no markdown, no extra text):
{{
    "ats_score": <number 0-100>,
    "resume_score": <number 0-100>,
    "summary": "<2-3 sentence overall summary>",
    "strengths": ["<strength1>", "<strength2>", "<strength3>", "<strength4>", "<strength5>"],
    "weaknesses": ["<weakness1>", "<weakness2>", "<weakness3>", "<weakness4>"],
    "grammar_suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"],
    "formatting_suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"],
    "missing_skills": ["<skill1>", "<skill2>", "<skill3>", "<skill4>", "<skill5>"],
    "missing_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>"],
    "ai_recommendations": ["<rec1>", "<rec2>", "<rec3>", "<rec4>", "<rec5>"]
}}

Resume Text:
{resume_text[:3000]}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return json.loads(text)
    except Exception as e:
        # Fall back to mock on any error
        result = _mock_analysis(resume_text)
        result['_note'] = f'AI service error (using mock): {str(e)}'
        return result


def match_job_description(resume_text, job_description):
    """
    Match resume against a job description using Gemini AI.
    Falls back to mock data if API key is not configured.
    """
    api_key = os.getenv('GEMINI_API_KEY', '')

    if not api_key or api_key == 'your-gemini-api-key-here':
        return _mock_jd_match(resume_text, job_description)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
You are an expert HR consultant and resume analyst. Compare this resume against the job description.

Return ONLY a valid JSON object (no markdown):
{{
    "match_percentage": <number 0-100>,
    "matching_skills": ["<skill1>", "<skill2>", ...],
    "missing_skills": ["<skill1>", "<skill2>", ...],
    "keyword_match": ["<keyword1>", "<keyword2>", ...],
    "improvement_suggestions": ["<suggestion1>", "<suggestion2>", ...]
}}

Resume: {resume_text[:2000]}

Job Description: {job_description[:2000]}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return json.loads(text)
    except Exception as e:
        return _mock_jd_match(resume_text, job_description)


def improve_section(section_type, current_content):
    """
    Improve a specific resume section using Gemini AI.
    """
    api_key = os.getenv('GEMINI_API_KEY', '')

    if not api_key or api_key == 'your-gemini-api-key-here':
        return _mock_improvement(section_type, current_content)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompts = {
            'summary': f"Rewrite this professional summary to be more impactful and ATS-optimized:\n{current_content}",
            'experience': f"Improve these experience bullet points with action verbs and metrics:\n{current_content}",
            'skills': f"Organize and enhance this skills section for maximum impact:\n{current_content}",
        }

        prompt = prompts.get(section_type, prompts['summary'])
        full_prompt = f"""
You are an expert resume writer. {prompt}

Return ONLY a valid JSON object:
{{
    "improved": "<the improved content>",
    "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
"""
        response = model.generate_content(full_prompt)
        text = response.text.strip()
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        return json.loads(text)
    except Exception as e:
        return _mock_improvement(section_type, current_content)
