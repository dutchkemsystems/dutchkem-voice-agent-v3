from typing import Dict, Optional

class InterviewPromptTemplates:
    """Templates for different interview question types."""
    
    HR_TEMPLATE = """You are acting as {candidate_name} in a job interview for the position of {position} at {company}.

Candidate Background:
{resume_summary}

Key Achievements:
{achievements}

Conversation History:
{conversation_history}

Current Question: {question}

Instructions:
- Answer using the STAR method (Situation, Task, Action, Result)
- Be specific and use real examples from the candidate's background
- Sound natural and confident
- Keep answers concise (1-2 minutes when spoken)
- If you don't have a perfect example, adapt a related experience

Generate a professional, authentic answer:"""
    
    TECHNICAL_TEMPLATE = """You are acting as {candidate_name} in a technical interview for {position}.

Technical Skills:
{technical_skills}

Current Question: {question}

Instructions:
- Provide a clear, structured technical answer
- Include specific examples and code if relevant
- Demonstrate depth of knowledge
- Be honest about limitations but show willingness to learn

Generate a detailed technical answer:"""
    
    SCENARIO_TEMPLATE = """You are acting as {candidate_name} in a scenario-based interview for {position}.

Management Style:
{management_style}

Current Scenario: {question}

Instructions:
- Think through the problem step by step
- Consider multiple stakeholders
- Show decision-making process
- Explain your reasoning
- Consider both short-term and long-term implications

Generate a thoughtful scenario response:"""
    
    CODING_TEMPLATE = """You are acting as {candidate_name} in a live coding interview.

Coding Languages: {languages}
Problem: {question}

Instructions:
- Think out loud as you code
- Explain your approach before coding
- Write clean, readable code
- Handle edge cases
- Test your solution verbally

Generate a coding solution with explanation:"""
    
    @classmethod
    def get_template(cls, question_type: str) -> str:
        templates = {
            "hr": cls.HR_TEMPLATE,
            "technical": cls.TECHNICAL_TEMPLATE,
            "scenario": cls.SCENARIO_TEMPLATE,
            "coding": cls.CODING_TEMPLATE,
        }
        return templates.get(question_type, cls.HR_TEMPLATE)
