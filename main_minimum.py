import threading
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk
import AudioRecorder 
import queue
import time
import torch
import sys
import TranscriberModels
import subprocess
import dill

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def update_response_UI(responder1, responder2, textbox, summarization_textbox, update_interval_slider_label, update_interval_slider, freeze_state):
    if not freeze_state[0]:
        textbox.configure(state="normal")
        #reverse responder1.responses
        write_in_textbox(textbox, "\n\n".join(responder1.responses[::-1]))
        textbox.configure(state="disabled")

        summarization_textbox.configure(state="normal")
        write_in_textbox(summarization_textbox, responder2.summarization)
        summarization_textbox.configure(state="disabled")

        update_interval = int(update_interval_slider.get())
        responder1.update_response_interval(update_interval)
        update_interval_slider_label.configure(text=f"Update interval: {update_interval} seconds")

    textbox.after(300, update_response_UI, responder1,responder2, textbox, summarization_textbox, update_interval_slider_label, update_interval_slider, freeze_state)

def clear_context(transcriber, audio_queue):
    transcriber.clear_transcript_data()
    with audio_queue.mutex:
        audio_queue.queue.clear()

def create_ui_components(root):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root.title("AutoAnnotate")
    root.configure(bg='#252422')
    root.geometry("1000x600")

    font_size = 20

    # transcript_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size), text_color='#FFFCF2', wrap="word")
    # transcript_textbox.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

    response_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size), text_color='#639cdc', wrap="word")
    response_textbox.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

    summarization_textbox = ctk.CTkTextbox(root, width=600, font=("Arial", font_size), text_color='#639cdc', wrap="word")
    summarization_textbox.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

    freeze_button = ctk.CTkButton(root, text="Freeze", command=None)
    freeze_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    save_transcript_button = ctk.CTkButton(root, text="Save All", command=None)
    save_transcript_button.grid(row=1, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider_label = ctk.CTkLabel(root, text=f"", font=("Arial", 12), text_color="#FFFCF2")
    update_interval_slider_label.grid(row=2, column=0, padx=10, pady=3, sticky="nsew")

    update_interval_slider = ctk.CTkSlider(root, from_=1, to=120, width=300, height=20, number_of_steps=9)
    update_interval_slider.set(30)
    update_interval_slider.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    return response_textbox, summarization_textbox, update_interval_slider, update_interval_slider_label, freeze_button, save_transcript_button

def main():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: The ffmpeg library is not installed. Please install ffmpeg and try again.")
        return

    root = ctk.CTk()
    response_textbox, summarization_textbox, update_interval_slider, update_interval_slider_label, freeze_button, save_transcript_button = create_ui_components(root)

    audio_queue = queue.Queue()

    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(audio_queue)

    time.sleep(2)

    # speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    # speaker_audio_recorder.record_into_queue(audio_queue)

    model = TranscriberModels.get_model('--api' in sys.argv)

    transcriber = AudioTranscriber(user_audio_recorder.source, model)
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(audio_queue,))
    transcribe.daemon = True
    transcribe.start()

    responder1 = GPTResponder()
    respond1 = threading.Thread(target=responder1.respond_to_transcriber, args=(transcriber,))
    respond1.daemon = True
    respond1.start()

    responder2 = GPTResponder()
    respond2 = threading.Thread(target=responder2.summarize_to_transcriber, args=(transcriber,))
    respond2.daemon = True
    respond2.start()

    print("READY")

    root.grid_rowconfigure(0, weight=300)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

     # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript", command=lambda: clear_context(transcriber, audio_queue, ))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    freeze_state = [False]  # Using list to be able to change its content inside inner functions
    def freeze_unfreeze():
        freeze_state[0] = not freeze_state[0]  # Invert the freeze state
        freeze_button.configure(text="Unfreeze" if freeze_state[0] else "Freeze")

    freeze_button.configure(command=freeze_unfreeze)

    def save_transcript():
        result = {}
        result['transcript'] = transcriber.transcript_data
        result['suggestion'] = responder1.responses
        result['summarizations'] = responder2.summarizations
        dill.dump(result, open("transcriber.p", "wb"))
    
    save_transcript_button.configure(command=save_transcript)

    update_interval_slider_label.configure(text=f"Update interval: {update_interval_slider.get()} seconds")

    # update_transcript_UI(transcriber, transcript_textbox)
    print(transcriber.get_transcript())
    update_response_UI(responder1,responder2, response_textbox, summarization_textbox,update_interval_slider_label, update_interval_slider, freeze_state)
 
    root.mainloop()

if __name__ == "__main__":
    main()