import re
from typing import Dict, List


def validate_registration_data(full_name: str, email: str, password: str, confirm_password: str) -> Dict[str, str]:
    errors = {}
    if not full_name or len(full_name.strip()) < 2:
        errors["full_name"] = "Enter your full name."

    if not email or "@" not in email or "." not in email:
        errors["email"] = "Enter a valid email address."

    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."

    if password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    return errors


def validate_login_data(email: str, password: str) -> Dict[str, str]:
    errors = {}
    if not email or "@" not in email or "." not in email:
        errors["email"] = "Enter a valid email address."
    if not password or len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    return errors


def analyze_resume_text(resume_text: str) -> Dict[str, object]:
    trimmed = resume_text.strip()
    if not trimmed:
        return {"score": 0, "strengths": [], "weaknesses": ["Resume text is empty."], "recommendations": ["Add your education and accomplishment details."]}

    lower = trimmed.lower()
    metrics_count = len(re.findall(r"\b\d+\b", lower))
    action_verbs = len(re.findall(r"\b(manage|created|improved|launched|developed|designed|implemented|led|built|analyzed|optimized)\b", lower))
    results_keywords = len(re.findall(r"\b(increased|improved|decreased|boosted|reduced|saved|grew|delivered|launched)\b", lower))
    length_score = min(20, len(trimmed.split()))
    keyword_score = sum(bool(re.search(fr"\b{word}\b", lower)) for word in ["product", "analysis", "lead", "team", "strategy", "results", "project", "launch"])

    score = min(100, max(35, int((length_score * 2.5) + action_verbs * 6 + results_keywords * 5 + keyword_score * 5 + min(metrics_count, 5) * 5)))

    strengths = [
        "The resume uses active achievement language." if action_verbs >= 2 else "Add stronger action verbs to describe your experience.",
        "Quantitative outcomes are present." if results_keywords >= 1 or metrics_count >= 1 else "Add metrics to show the impact of your work.",
    ]

    weaknesses: List[str] = []
    if len(trimmed.split()) < 120:
        weaknesses.append("The resume is concise but may need more detail for career transition.")
    if "led" not in lower and "managed" not in lower:
        weaknesses.append("Consider highlighting leadership or project ownership.")
    if "product" not in lower and "strategy" not in lower and "analysis" not in lower:
        weaknesses.append("Include role-specific keywords based on your target job.")
    if not weaknesses:
        weaknesses.append("The resume content is clear and focused.")

    recommendations: List[str] = []
    if action_verbs < 4:
        recommendations.append("Use more measurable verbs to describe accomplishments.")
    else:
        recommendations.append("Continue using impact statements with strong verbs.")
    if metrics_count < 2:
        recommendations.append("Add numbers to show the scale and impact of your work.")
    if keyword_score < 3:
        recommendations.append("Tailor your content to job-specific keyword themes.")
    else:
        recommendations.append("Your resume matches strong role themes.")

    strengths = [item for item in strengths if item]
    recommendations = [item for item in recommendations if item]

    if not strengths:
        strengths = ["Your resume has a professional structure."]
    if not recommendations:
        recommendations = ["Keep refining your experience with measurable detail."]

    return {
        "score": score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
    }


def generate_chat_response(question: str) -> str:
    text = question.strip().lower()
    if not text:
        return "Tell me a little more about your career question so I can suggest a helpful next step."

    guidance_signals = {
        "resume": "A strong resume should emphasize results, role context, and a concise summary of impact.",
        "interview": "Prepare by practicing STAR stories for your top three achievements and explain what you learned.",
        "skills": "Focus on one or two high-impact skills and show how you used them in real projects.",
        "career": "Map your next role with a three-month roadmap that includes a portfolio update and networking plan.",
        "application": "Match your bullet points to the job description and keep the narrative consistent.",
        "job": "Target roles that align with your strongest experiences and refine your resume for each role.",
    }

    for keyword, answer in guidance_signals.items():
        if keyword in text:
            return answer

    if "help" in text or "what" in text or "how" in text:
        return "I suggest starting with your strongest project and turning it into a concise story with clear business outcomes."

    if len(text.split()) <= 5:
        return "Send me a more detailed question about your resume, interview, or next career step."

    return "This looks solid. I recommend focusing on outcomes and making your next role the logical next step for the story you tell."