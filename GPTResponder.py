import openai
from keys import OPENAI_API_KEY
from prompts import create_suggestion, create_summarization
import time

openai.api_key = OPENAI_API_KEY

# def generate_response_from_transcript(transcript):
#     try:
#         response = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[{"role": "system", "content": create_prompt(transcript)}],
#                 temperature = 0.0
#         )
#     except Exception as e:
#         print(e)
#         return ''
#     full_response = response.choices[0].message.content
#     print(response.choices[0])
#     try:
#         return full_response.split('[')[1].split(']')[0]
#     except:
#         return ''
def generate_suggestion_from_transcript(transcript):
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": create_suggestion(transcript)}],
                temperature = 0.0
        )
    except Exception as e:
        print(e)
        return ''
    full_response = response.choices[0].message.content
    print("suggestion:" + full_response)
    try:
        return full_response
    except:
        return ''
    
def generate_summarization_from_transcript(transcript):
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": create_summarization(transcript)}],
                temperature = 0.0
        )
    except Exception as e:
        print(e)
        return ''
    full_response = response.choices[0].message.content
    print("summarization:" + full_response)
    try:
        return full_response
    except:
        return ''
    
class GPTResponder:
    def __init__(self):
        self.responses = []
        self.response_interval = 30
        self.summarization_interval = 90
        self.summarization = ''
        self.summarizations = []

    def respond_to_transcriber(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear() 
                transcript_string = transcriber.get_transcript()
                response = generate_suggestion_from_transcript(transcript_string)
                
                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate the time it took to execute the function
                
                if response != '':
                    if response not in self.responses:
                        self.responses.append(response)

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def summarize_to_transcriber(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear() 
                transcript_string = transcriber.get_transcript()
                response = generate_summarization_from_transcript(transcript_string)
                
                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate the time it took to execute the function
                
                if response != '':
                    self.summarization = response
                    self.summarizations.append(response)

                remaining_time = self.summarization_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def update_response_interval(self, interval):
        self.response_interval = interval