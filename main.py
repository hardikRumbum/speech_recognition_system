# Import necessary libraries
import os
import signal
from threading import Thread
from queue import Queue
import speech_recognition as sr

# Initialize the Speech Recognition module and create a queue to store audio data
r = sr.Recognizer()
audio_queue = Queue()

# Define a function to gracefully terminate the script
def terminate_script():
    # Get the current process ID
    pid = os.getpid()

    # Terminate the script gracefully
    os.kill(pid, signal.SIGTERM)

# Define a function to run in the background thread and process audio data
def recognize_worker():
    print("Speak now...")
    # This function runs in a background thread
    while True:
        # Retrieve the next audio processing job from the main thread
        audio = audio_queue.get()

        # If the main thread is done, stop processing
        if audio is None:
            break

        try:
            # Recognize speech in the audio data using Google Speech Recognition
            text = r.recognize_google(audio)

            # Print the recognized text
            print(f"You speak : {text}")

            # If the recognized text is "stop", gracefully terminate the script
            if text == "stop":
                print("Script stopped")
                terminate_script()

        except sr.UnknownValueError:
            # If the Speech Recognition API cannot understand the audio, ignore and continue
            pass
        except sr.RequestError as e:
            # If there is an error making a request to the Speech Recognition API, print the error message
            print("Could not request results from voice; {0}".format(e))

        # Mark the audio processing job as completed in the queue
        audio_queue.task_done()

# Start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()

# Use the microphone as the source of audio data and put the resulting audio on the audio processing job queue
with sr.Microphone() as source:
    try:
        while True:
            # Repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:
        # Allow Ctrl + C to shut down the program
        pass

# Block until all current audio processing jobs are done
audio_queue.join()

# Tell the recognize_thread to stop by putting None into the queue
audio_queue.put(None)

# Wait for the recognize_thread to actually stop
recognize_thread.join()