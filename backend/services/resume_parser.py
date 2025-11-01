import os
import re
import json
import logging
import PyPDF2
import docx
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse resumes and extract structured information using LLM"""

    def __init__(
        self,
        model_name: str = "llama3:instruct",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume file and extract structured candidate information.
        Returns parsed_data and confidence scores.
        """
        try:
            # Step 1: Extract text
            text = self._extract_text(file_path)
            if not text or len(text.strip()) < 50:
                raise ValueError("Could not extract sufficient text from resume")

            # Step 2: LLM-based extraction
            llm_result = self._extract_with_llm(text)
            basic_result = self._basic_extraction(text)

            parsed_data = llm_result.get("parsed_data", {})
            confidence = llm_result.get("confidence", {})

            # Step 3: Merge fallback values
            for k, v in basic_result.items():
                if not parsed_data.get(k):
                    parsed_data[k] = v
                    confidence[k] = confidence.get(k, 0.4)  # heuristic fallback confidence

            # Step 4: Clean up confidence (default 0.5 for missing)
            for k in parsed_data.keys():
                if k not in confidence:
                    confidence[k] = 0.5

            logger.info(f"Resume parsed successfully: {file_path}")
            return {"parsed_data": parsed_data, "confidence": confidence}

        except ValueError as ve:
            logger.warning(f"Validation error while parsing resume {file_path}: {ve}")
            return {"parsed_data": {}, "confidence": {}, "error": str(ve)}

        except Exception as e:
            logger.error(f"Unexpected error while parsing resume {file_path}: {e}", exc_info=True)
            return {"parsed_data": {}, "confidence": {}, "error": "Internal parsing error"}

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._extract_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            raise

#     def _extract_with_llm(self, text: str) -> Dict[str, Any]:
#         """Use Ollama LLM to extract structured data"""

#         logger.info("extracting using llms")

#         prompt = f"""Extract the following information from this resume and return ONLY a valid JSON object with no additional text or markdown formatting:

# Resume Text:
# {text[:4000]}  

# Extract these fields:
# - name: Full name of the candidate
# - email: Email address
# - phone: Phone number
# - current_company: Current or most recent company
# - designation: Current or most recent job title
# - skills: Array of technical and professional skills
# - experience_years: Total years of experience (as a number)
# - education: Highest degree
# - location: Current location

# Return ONLY a JSON object with these exact keys. Example format:
# {{"name": "John Doe", "email": "john@example.com", "phone": "+1234567890", "current_company": "Tech Corp", "designation": "Senior Engineer", "skills": ["Python", "AWS"], "experience_years": 5, "education": "B.Tech Computer Science", "location": "Mumbai"}}"""

#         try:
#             response = requests.post(
#                 self.api_url,
#                 json={
#                     "model": self.model_name,
#                     "prompt": prompt,
#                     "stream": False,
#                     "options": {"temperature": 0.1, "top_p": 0.9},
#                 },
#                 timeout=60,
#             )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 generated_text = result.get("response", "").strip()

#                 # Try to extract JSON from response
#                 json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
#                 if json_match:
#                     json_str = json_match.group()
#                     parsed_data = json.loads(json_str)

#                     # Validate and clean data
#                     cleaned_data = self._clean_extracted_data(parsed_data)
#                     return cleaned_data
#                 else:
#                     logger.warning("No JSON found in LLM response")
#                     return {}
#             else:
#                 logger.error(f"Ollama API error: {response.status_code}")
#                 logger.error(f"error: {response}")
#                 return {}

#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error calling Ollama API: {str(e)}")
#             return {}
#         except json.JSONDecodeError as e:
#             logger.error(f"Error parsing JSON from LLM: {str(e)}")
#             return {}
#         except Exception as e:
#             logger.error(f"Unexpected error in LLM extraction: {str(e)}")
#             return {}

    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """Use Ollama LLM to extract structured data with confidence scores"""

        logger.info("extracting using llms")

        prompt = f"""
        You are a resume parser. Extract the following information as a JSON object.
        For each field, include a confidence score (0 to 1) indicating how sure you are.

        Resume Text:
        {text[:4000]}

        Fields:
        - name
        - email
        - phone
        - current_company
        - designation
        - skills (array)
        - experience_years (number)
        - education
        - location

        Output format (strict JSON only, no extra text):
        {{
        "fields": {{
            "name": {{"value": "John Doe", "confidence": 0.95}},
            "email": {{"value": "john@example.com", "confidence": 0.98}},
            "phone": {{"value": "+123456789", "confidence": 0.85}},
            "current_company": {{"value": "Tech Corp", "confidence": 0.88}},
            "designation": {{"value": "Software Engineer", "confidence": 0.9}},
            "skills": {{"value": ["Python", "AWS"], "confidence": 0.92}},
            "experience_years": {{"value": 5, "confidence": 0.9}},
            "education": {{"value": "B.Tech Computer Science", "confidence": 0.93}},
            "location": {{"value": "Bangalore", "confidence": 0.87}}
        }}
        }}
        """

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "top_p": 0.9},
                },
                timeout=90,
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)

                if not json_match:
                    logger.warning("No JSON found in LLM response")
                    return {}

                parsed = json.loads(json_match.group())
                fields = parsed.get("fields", {})

                cleaned_data = {}
                confidence_data = {}

                for key, val in fields.items():
                    cleaned_data[key] = val.get("value")
                    confidence_data[key] = val.get("confidence", 0.5)

                return {"parsed_data": cleaned_data, "confidence": confidence_data}

            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Error in _extract_with_llm: {e}", exc_info=True)
            return {}


    def _basic_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback: Basic regex-based extraction"""

        result = {
            "name": None,
            "email": None,
            "phone": None,
            "current_company": None,
            "designation": None,
            "skills": [],
            "experience_years": None,
            "education": None,
            "location": None,
        }

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        if emails:
            result["email"] = emails[0]

        # Extract phone (Indian format)
        phone_pattern = r"[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}"
        phones = re.findall(phone_pattern, text)
        if phones:
            result["phone"] = phones[0].strip()

        # Extract common skills
        common_skills = [
            "Python",
            "Java",
            "JavaScript",
            "React",
            "Node.js",
            "AWS",
            "Docker",
            "Kubernetes",
            "SQL",
            "MongoDB",
            "Git",
            "Machine Learning",
            "AI",
            "Flask",
            "Django",
            "Spring",
            "Angular",
            "Vue",
            "TypeScript",
        ]

        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        result["skills"] = found_skills

        return result

    def _clean_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate extracted data"""

        cleaned = {}

        # String fields
        for field in [
            "name",
            "email",
            "phone",
            "current_company",
            "designation",
            "education",
            "location",
        ]:
            value = data.get(field)
            if value and isinstance(value, str):
                cleaned[field] = value.strip()
            else:
                cleaned[field] = None

        # Skills array
        skills = data.get("skills", [])
        if isinstance(skills, list):
            cleaned["skills"] = [str(s).strip() for s in skills if s]
        else:
            cleaned["skills"] = []

        # Experience years
        exp = data.get("experience_years")
        if isinstance(exp, (int, float)):
            cleaned["experience_years"] = int(exp)
        elif isinstance(exp, str):
            # Try to extract number from string
            numbers = re.findall(r"\d+", exp)
            if numbers:
                cleaned["experience_years"] = int(numbers[0])
            else:
                cleaned["experience_years"] = None
        else:
            cleaned["experience_years"] = None

        return cleaned
