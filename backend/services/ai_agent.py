"""
AI Agent for generating personalized document requests
"""

import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(f"{__name__}.AIAgent")


class AIAgent:
    """AI Agent that generates personalized communication"""

    def __init__(
        self,
        model_name: str = "llama3:instruct",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def generate_document_request(self, candidate_data: Dict[str, Any]) -> str:
        """
        Generate a personalized document request message

        Args:
            candidate_data: Dictionary containing candidate information

        Returns:
            Personalized message string
        """

        name = candidate_data.get("name", "Candidate")
        email = candidate_data.get("email", "")
        phone = candidate_data.get("phone", "")
        designation = candidate_data.get("designation", "Professional")
        company = candidate_data.get("current_company", "")

        # Build context for the AI
        sender_email = "hr@hiring.com" 
        sender_name = "Hiring Team"  

        context = f"""You are an HR assistant generating a personalised, short, professional and polite message.

Task: Write ONLY the document request message body. 
Do NOT include any headings, labels, or introductions such as "Here is the message" or "Status: sent". 
Output only the clean message body, no markdown, no bullet points, and no metadata.

Use this candidate info:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Current Role: {designation}
- Company: {company}

Requirements:
1. Address the candidate by name (e.g., "Dear {name},").
2. Politely request PAN card and Aadhaar card for identity verification for HR records.
3. Ask them to send these documents to {sender_email}.
4. Mention accepted formats: PDF, JPG, PNG.
5. Keep it concise (5-6 short lines total).
6. End with "Best regards," and "{sender_name}".
7. DO NOT use the candidate's email address as a destination or in a mailto link.
8. DO NOT include any additional commentary or labels.

Return ONLY the clean message text (no code block, no quotes, no explanations).
"""
        logger.info(f"sending context {context}")
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": context,
                    "stream": False,
                    "options": {"temperature": 0.2, "top_p": 0.9, "max_tokens": 500},
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                message = result.get("response", "").strip()

                if message:
                    return message
                else:
                    # Fallback to template
                    return self._generate_template_message(candidate_data)
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._generate_template_message(candidate_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            return self._generate_template_message(candidate_data)
        except Exception as e:
            logger.error(f"Unexpected error generating request: {str(e)}")
            return self._generate_template_message(candidate_data)

    def _generate_template_message(self, candidate_data: Dict[str, Any]) -> str:
        """Fallback template-based message generation"""

        name = candidate_data.get("name", "Candidate")

        message = f"""Dear {name},

Thank you for your interest in joining our organization. As part of our verification process, we kindly request you to submit the following identity documents:

1. PAN Card (Permanent Account Number)
2. Aadhaar Card

These documents are required for identity verification and maintaining accurate HR records. Please ensure the documents are clear and legible.

Submission Instructions:
- Accepted formats: PDF, JPG, or PNG
- Maximum file size: 5MB per document
- Please submit both documents at your earliest convenience

You can upload the documents through our portal or reply to this message with the attachments.

If you have any questions or concerns, please feel free to reach out to us.

Best regards,
HR Team"""

        return message

    def generate_followup_message(
        self, candidate_data: Dict[str, Any], missing_docs: list
    ) -> str:
        """
        Generate a follow-up message for missing documents

        Args:
            candidate_data: Candidate information
            missing_docs: List of missing document types

        Returns:
            Follow-up message string
        """

        name = candidate_data.get("name", "Candidate")
        docs_str = " and ".join(missing_docs).upper()

        prompt = f"""Generate a polite follow-up message to request missing documents from a candidate.

Candidate Name: {name}
Missing Documents: {docs_str}

The message should:
1. Be friendly and non-pushy
2. Remind them of the missing documents
3. Offer assistance if they're facing issues
4. Keep it brief (2-3 paragraphs)

Generate ONLY the message content."""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "top_p": 0.9},
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return self._generate_template_followup(name, missing_docs)

        except Exception as e:
            logger.error(f"Error generating follow-up: {str(e)}")
            return self._generate_template_followup(name, missing_docs)

    def _generate_template_followup(self, name: str, missing_docs: list) -> str:
        """Template-based follow-up message"""

        docs_str = " and ".join(missing_docs).upper()

        return f"""Dear {name},

We noticed that we haven't received your {docs_str} yet. This is a gentle reminder to submit these documents at your earliest convenience to complete your verification process.

If you're experiencing any difficulties with the submission or have any questions, please don't hesitate to contact us. We're here to help!

Thank you for your cooperation.

Best regards,
HR Team"""
