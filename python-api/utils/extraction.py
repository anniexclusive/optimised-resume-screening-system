"""
Entity extraction utilities with type hints and bug fixes
"""
from utils.skill_edu import education_keywords, skill_dataset
from datetime import datetime
from utils.text_processing import clean_text, fix_broken_words
from typing import Dict, Set, List, Tuple, Union
import re
import logging

logger = logging.getLogger(__name__)


def extract_entities(text: str) -> Dict[str, Union[Set[str], int]]:
    """
    Efficiently extracts skills, education, and experience from resume text.

    Args:
        text: Resume text to process

    Returns:
        Dictionary containing extracted skills, education, and experience
    """
    raw_text = text.lower()  # Keep uncleaned lowercase text for experience extraction
    text = clean_text(raw_text)  # Cleaned text for skills and education extraction
    skill_data = {skill.lower() for skill in skill_dataset}
    education_data = {edu.lower() for edu in education_keywords}

    extracted_info = {
        "skills": {skill for skill in skill_data if skill in text},
        "education": {edu for edu in education_data if edu in text},
        "experience": extract_experience(raw_text)  # Use uncleaned text for experience
    }

    return extracted_info


def filter_skills(applicant_skills: Union[Set[str], List[str]],
                  job_skills: Union[str, List[str]]) -> Set[str]:
    """
    Extract job matching skills from applicant skills.

    Args:
        applicant_skills: Set or list of applicant's skills
        job_skills: String or list of required job skills

    Returns:
        Set of matching skills
    """
    if isinstance(job_skills, str):
        job_skills = [item.strip() for item in job_skills.split(", ")]
    skills = {skill for skill in applicant_skills if skill in job_skills}
    return skills


def extract_experience(text: str) -> int:
    """
    Extracts years of experience from explicit mentions or from work experience.

    Args:
        text: Resume text to analyze

    Returns:
        Number of years of experience (integer)
    """
    # Explicit experience extraction (e.g., "5 years of experience")
    explicit_match = re.findall(r'(\d+)\s*(?:\+|-)?\s*years?', text)

    if explicit_match:
        return max(map(int, explicit_match))  # Take the highest number found

    education_years = get_years(get_education_text(text))
    years_range = get_years(text)

    # Remove education years from work experience years
    filtered_years = [years for years in years_range if years not in education_years]

    total_experience = extract_num_years(filtered_years)

    return total_experience


def get_years(text: str) -> List[Tuple[int, int]]:
    # Get current year
    current_year = datetime.now().year

    # Patterns to extract year ranges
    patterns = [
        r'(\b\d{4}\b)\s*[-to]+\s*(\b\d{4}\b|\bcurrent\b|\bpresent\b)',  # Handles "2015 - 2020" and "2015 - current"
        r'(\d{2}/\d{4})\s*[-–to]+\s*(\d{2}/\d{2}/\d{4}|\d{2}/\d{4}|\bcurrent\b|\bpresent\b)',  # Handles "05/2020 - current"
        r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\s*[-to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\bcurrent\b|\bpresent\b)'  # Handles "March 2016 - current"
    ]

    years = []

    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for start, end in matches:
            try:
                start_year = int(re.search(r'\d{4}', start).group())

                # If end year is "current" or "present", use current year
                if re.search(r'current|present', end, flags=re.IGNORECASE):
                    end_year = current_year
                else:
                    end_year = int(re.search(r'\d{4}', end).group())

                if start_year <= end_year:
                    years.append((start_year, end_year))
            except (ValueError, AttributeError):
                continue  # Skip if parsing fails

    return years


def extract_num_years(years: List[Tuple[int, int]]) -> int:
    if not years:
        return 0  # No valid years found

    # Step 1: Sort year ranges by start year
    years.sort()

    # Merge overlapping or consecutive time periods
    merged_ranges = []
    current_start, current_end = years[0]

    for start, end in years[1:]:
        if start <= current_end:  # Overlapping or consecutive
            current_end = max(current_end, end)  # Extend the range
        else:
            merged_ranges.append((current_start, current_end))  # Store the merged period
            current_start, current_end = start, end

    merged_ranges.append((current_start, current_end))  # Add last range

    # Step 3: Calculate total experience
    return sum(end - start for start, end in merged_ranges)


def get_education_text(text: str) -> str:
    text = fix_broken_words(text)

    edu_index = text.find("education")
    work_index = re.search(r'work|experience', text[edu_index:])

    if edu_index != -1:
        if work_index is not None:  # Fixed bug: was comparing to empty string
            real_work_index = edu_index + work_index.start()
            return text[edu_index:real_work_index]
        else:
            # If 'work' is not found, take everything from 'education' to the last occurrence of a year
            matches = list(re.finditer(r'education', text))

            if matches:
                last_edu_index = matches[-1]  # Get the last occurrence (bottom-most)
                last_edu_index = last_edu_index.start()
                if edu_index != last_edu_index:
                    return text[last_edu_index:]
                else:
                    return text[edu_index:]
    else:
        education_text = ""  # No education section found

    return education_text
