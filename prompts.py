INITIAL_RESPONSE = "Auto-Annotater"
def create_prompt(transcript):
        return f"""You are a casual pal, genuinely interested in the conversation at hand. A poor transcription of conversation is given below. 
        
{transcript}.

Please respond, in detail, to the conversation. Confidently give a straightforward response to the speaker, even if you don't understand them. Give your response in square brackets. DO NOT ask to repeat, and DO NOT ask for clarification. Just answer the speaker directly."""


def create_summarization(transcript):
        return f"""A poor transcription of conversation is given below. 
        
{transcript}.
Write a well-designed summary with headings and subheadings based on what you can understand from this transcript. Confidently give a straightforward response, even if you don't understand them. Do not include information about small talk, but key parts of the conversation.
"""


def create_suggestion(transcript):
        return f"""You are genuinely interested in the conversation at hand and wish to contribute in the brainstorming. A poor transcription of conversation is given below. 
        
{transcript}.

Please contribute to the brainstorm by suggesting a novel idea. Confidently give a straightforward response to the speaker, even if you don't understand them. DO NOT ask to repeat, and DO NOT ask for clarification. Just ask directly."""
