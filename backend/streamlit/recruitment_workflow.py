import re
from src.utils.llm import call_llm

def classify_domain(cv_text: str) -> str:
    """Classify the main technology/domain of a CV using LLM."""
    prompt = [
        {"role": "system", "content": (
            "You are an expert recruiter. "
            "Read the CV and classify the **main technology/domain** into one label "
            "(e.g., Python, Data Science, Frontend, Backend, Cloud, DevOps, HR, Project Manager, Business Analyst, Business Development, Marketing, Sales, Finance, Legal, etc.). "
            "Respond with only the label."
        )},
        {"role": "user", "content": cv_text}
    ]
    response = call_llm(prompt)
    return response.choices[0].message.content.strip()

def match_requirements(domain: str, open_requirements=None) -> tuple[bool, str]:
    """
    Ask the LLM if the domain matches any open requirement.
    Returns (matched, matched_role).
    """
    open_requirements = open_requirements or [
        "Python Developer", "Data Scientist", "Frontend Engineer", "Backend Engineer", "Cloud Engineer", "HR Manager,  Project Manager, Business Analyst"
    ]

    prompt = [
        {"role": "system", "content": (
            "You are a recruitment assistant. "
            "Check if the given candidate domain matches one of the open requirements. "
            "If yes, respond with the matched requirement inside <matched_role> tags. If not, respond with <matched_role>No match</matched_role> and provide the closest match inside <closest_match> tags. Provide the reasoning for the match or closest match inside <reasoning> tags."
        )},
        {"role": "user", "content": f"Candidate domain: {domain}\nOpen roles: {', '.join(open_requirements)}"}
    ]
    response = call_llm(prompt)
    result = response.choices[0].message.content.strip()

    matched_role =re.search(r"<matched_role>(.*?)</matched_role>", result)
    closest_match =re.search(r"<closest_match>(.*?)</closest_match>", result)
    reasoning =re.search(r"<reasoning>(.*?)</reasoning>", result)
    
    print(result)
    if matched_role and matched_role.group(1).lower() != "no match":
        return True, matched_role.group(1), reasoning.group(1)
    elif closest_match:
        return False, closest_match.group(1), reasoning.group(1)
    else:
        return False, "No match", "No Match"

def write_email(cv_text: str, domain: str, matched_role: str, reasoning: str) -> str:
    """Ask LLM to draft a short recruiter email."""
    prompt = [
        {"role": "system", "content": (
            f"Write a short, professional email to the hiring manager recommending this CV who has domain: {domain} and has matched role: {matched_role} against open requirements, the match reasoning provided from the Matcher is: {reasoning}. Be polite and concise (3-4 sentences)."
        )},
        {"role": "user", "content": cv_text}
    ]
    response = call_llm(prompt)
    return response.choices[0].message.content.strip()

def send_email(email_address: str, email_text: str) -> str:
    """Send Email to Hiring Manager"""
    # send email to email_address with email_text
    print(f"Sending email to {email_address} with text: {email_text}")
    return "Email sent successfully"

def recruitment_workflow(cv_text: str) -> dict:
    """Run the recruitment workflow step by step with real LLM calls."""
    steps = {}

    # Step 1: classify
    domain = classify_domain(cv_text)
    steps["domain"] = domain

    # Step 2: check match
    matched, matched_role, reasoning = match_requirements(domain)
    steps["matched"] = matched
    steps["matched_role"] = matched_role
    steps["reasoning"] = reasoning

    # Step 3: email draft
    email = write_email(cv_text, domain, matched_role, reasoning)
    steps["email"] = email
    
    email_address = "hiring-manager@example.com"
    # Step 4: send email
    send_email(email_address, email)
    steps["email_sent"] = True

    return steps
