import win32com.client
import time

speaker = win32com.client.Dispatch("SAPI.SpVoice")

print("Test 1")
speaker.Speak("Hello this is test one.")
time.sleep(1)

print("Test 2")
speaker.Speak("Hello this is test two.")
time.sleep(1)

print("Test 3")
speaker.Speak("Hello this is test three.")

print("Done.")