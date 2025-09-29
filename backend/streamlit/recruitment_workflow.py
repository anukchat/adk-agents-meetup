from src.utils.llm import call_llm

def classify_domain(cv_text: str) -> str:
    """Classify the main technology/domain of a CV using LLM."""
    prompt = [
        {"role": "system", "content": (
            "You are an expert recruiter. "
            "Read the CV and classify the **main technology/domain** into one label "
            "(e.g., Python, Data Science, Frontend, Backend, Cloud, DevOps, etc.). "
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
        "Python Developer", "Data Scientist", "Frontend Engineer", "Backend Engineer", "Cloud Engineer", "HR Manager"
    ]

    prompt = [
        {"role": "system", "content": (
            "You are a recruitment assistant. "
            "Check if the given candidate domain matches one of the open requirements. "
            "If yes, respond with the matched requirement. If not, respond with 'No Match'."
        )},
        {"role": "user", "content": f"Candidate domain: {domain}\nOpen roles: {', '.join(open_requirements)}"}
    ]
    response = call_llm(prompt)
    result = response.choices[0].message.content.strip()

    if result.lower() == "no match":
        return False, None
    else:
        return True, result

def write_email(cv_text: str, domain: str, role: str) -> str:
    """Ask LLM to draft a short recruiter email."""
    prompt = [
        {"role": "system", "content": (
            "Write a short, professional email to the hiring manager recommending this CV "
            f"for the {role} role. Be polite and concise (3-4 sentences)."
        )},
        {"role": "user", "content": cv_text}
    ]
    response = call_llm(prompt)
    return response.choices[0].message.content.strip()

def recruitment_workflow(cv_text: str) -> dict:
    """Run the recruitment workflow step by step with real LLM calls."""
    steps = {}

    # Step 1: classify
    domain = classify_domain(cv_text)
    steps["domain"] = domain

    # Step 2: check match
    matched, matched_role = match_requirements(domain)
    steps["matched"] = matched
    steps["matched_role"] = matched_role

    # Step 3: email draft
    email = write_email(cv_text, domain, matched_role) if matched else None
    steps["email"] = email

    return steps
