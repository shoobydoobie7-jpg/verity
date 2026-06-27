import tkinter as tk
from datetime import datetime
import subprocess
import os
import threading
from PIL import Image, ImageTk
from duckduckgo_search import DDGS
import speech_recognition as sr
from playsound import playsound

class VerityAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Verity")
        
        # Hide the main primary window frame completely
        self.root.attributes("-alpha", 0.0) 
        
        # Create the transparent overlay face layer
        self.face_win = tk.Toplevel(self.root)
        self.face_win.title("Verity")
        self.face_win.overrideredirect(True)
        self.face_win.attributes("-topmost", True)
        self.face_win.config(bg='gray')
        self.face_win.attributes("-transparentcolor", 'gray')
        
        # Position Verity in the bottom right corner above the taskbar
        screen_width = self.face_win.winfo_screenwidth()
        screen_height = self.face_win.winfo_screenheight()
        self.face_win.geometry(f"200x250+{screen_width - 250}+{screen_height - 350}")

        self.canvas = tk.Canvas(self.face_win, width=200, height=200, bg='gray', highlightthickness=0)
        self.canvas.pack()
        
        self.p_img_normal = None
        self.p_img_creepy = None
        self.using_images = False

        # Filter and load custom JPEG textures
        self.load_images_with_transparency()

        if self.using_images:
            self.face_sprite = self.canvas.create_image(100, 100, image=self.p_img_normal)
        else:
            self.draw_vector_face()

        # Build UI items and click-drag controls
        self.setup_ui_and_bindings()
        
        # Start background voice recognition engine
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.voice_thread = threading.Thread(target=self.listen_for_keyword, daemon=True)
            self.voice_thread.start()
        except Exception as e:
            print(f"Microphone initialization skipped or unavailable: {e}")
            
        self.root.after(1000, self.greet)

    def load_images_with_transparency(self):
        TOLERANCE = 15
        face_images = {"normal": "normal.jpeg", "creepy": "creepy.jpeg"}
        if [f for f in face_images.values() if not os.path.exists(f)]:
            return
        
        def process_one_image(filename):
            img = Image.open(filename).convert("RGBA")
            datas = img.getdata()
            newData = []
            for item in datas:
                if item[0] > (255 - TOLERANCE) and item[1] > (255 - TOLERANCE) and item[2] > (255 - TOLERANCE):
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)
            img.putdata(newData)
            return img.resize((200, 200), Image.Resampling.LANCZOS)

        try:
            self.p_img_normal = ImageTk.PhotoImage(process_one_image(face_images["normal"]))
            self.p_img_creepy = ImageTk.PhotoImage(process_one_image(face_images["creepy"]))
            self.using_images = True
        except Exception:
            self.using_images = False

    def setup_ui_and_bindings(self):
        self.entry = tk.Entry(self.face_win, width=20, font=("Arial", 10))
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", lambda e: self.process_query(self.entry.get()))
        self.entry.insert(0, "Say 'Verity' or type...")
        self.entry.bind("<FocusIn>", lambda e: self.entry.delete(0, tk.END))
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_window)

    def draw_vector_face(self):
        self.face = self.canvas.create_oval(20, 20, 180, 180, fill="#FFD700", outline="#B8860B", width=4)
        self.smile = self.canvas.create_arc(50, 80, 150, 150, start=0, extent=-180, fill="black")

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def drag_window(self, event):
        x = self.face_win.winfo_x() + (event.x - self.x)
        y = self.face_win.winfo_y() + (event.y - self.y)
        self.face_win.geometry(f"+{x}+{y}")

    def speak(self, text):
        try:
            print(f"Verity says: {text}") 
            clean_text = text.replace('"', '').replace("'", "")
            ps_command = f'Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Speak("{clean_text}")'
            subprocess.Popen(["powershell", "-Command", ps_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
        except Exception:
            pass

    def greet(self):
        if os.path.exists("hi_verity.wav"):
            playsound("hi_verity.wav", block=False)
        else:
            self.speak("Hello! I'm Verity, your personal helper friend. ask me anything. I know everything")

    def listen_for_keyword(self):
        while True:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, phrase_time_limit=5)
                speech_text = self.recognizer.recognize_google(audio).lower()
                
                if "verity" in speech_text:
                    clean_question = speech_text.replace("verity", "").strip()
                    if clean_question:
                        self.root.after(0, self.process_query, clean_question)
                    else:
                        self.root.after(0, self.speak, "Yes? I am listening.")
            except sr.UnknownValueError:
                continue
            except Exception:
                continue

    def process_query(self, raw_query):
        query = raw_query.strip().lower()
        self.entry.delete(0, tk.END)
        print(f"Processing command: {query}")
        
        # ==========================================================
        # 1. SPECIAL MOD WAV AUDIO EASTER EGG TRIGGERS
        # ==========================================================
        if "hello" in query or "hi verity" in query or "who are you" in query:
            if os.path.exists("hi_verity.wav"):
                playsound("hi_verity.wav", block=False)
            else:
                self.speak("Hello! I'm Verity, your personal helper friend.")
                
        elif "villager" in query or "where is everyone" in query or "town" in query:
            if os.path.exists("villagers_gone.wav"):
                playsound("villagers_gone.wav", block=False)
            else:
                self.speak("The villagers? They are gone, Mob. You don't need them anymore.")

        # Clip C: My Gal Song (Added extra voice triggers)
        elif any(word in query for word in ["play music", "play a song", "my gal", "my girl", "play a tune", "do you kill people"]):
            if os.path.exists("my_gal.wav"):
                playsound("my_gal.wav", block=False)
            else:
                self.speak("Playing my favorite song! I hope you like old tunes.")

        elif "what is coming" in query or "three days" in query or "dangerous" in query:
            if self.using_images:
                self.canvas.itemconfig(self.face_sprite, image=self.p_img_creepy)
            else:
                self.canvas.itemconfig(self.face, fill="#8B0000")
            
            if os.path.exists("three_days.wav"):
                playsound("three_days.wav", block=False)
            else:
                self.speak("Something is coming in three days. You could have stopped it... but it's already too late.")
            
            def reset_face():
                if self.using_images:
                    self.canvas.itemconfig(self.face_sprite, image=self.p_img_normal)
                else:
                    self.canvas.itemconfig(self.face, fill="#FFD700")
            self.root.after(3000, reset_face)
            
        elif "time" in query:
            self.speak(f"It is currently {datetime.now().strftime('%I:%M %p')}. Time is running out, Mob.")

        # ==========================================================
        # 2. LOCAL INTUITIVE MATHEMATICS RESOLVER
        # ==========================================================
        elif any(char in query for char in ["+", "-", "*", "/", "plus", "minus", "times", "divided by"]):
            try:
                math_query = query.replace("plus", "+").replace("minus", "-").replace("times", "*").replace("divided by", "/")
                clean_math = "".join(c for c in math_query if c in "0123456789+-*/.()")
                result = eval(clean_math)
                self.speak(f"The answer is {result}.")
            except Exception:
                self.speak("That math problem looks a bit scrambled.")

        # ==========================================================
        # 3. INTERNET SCRAPER SEARCH ENHANCEMENT
        # ==========================================================
        else:
            try:
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=2))
                    if search_results and 'body' in search_results[0]:
                        response = search_results[0]['body']
                        sentences = response.split('. ')
                        response = ". ".join(sentences[:2]) + "."
                    else:
                        response = f"I couldn't locate any records for that topic."
            except Exception:
                response = "My background connection timed out."
            
            self.speak(response)

if __name__ == "__main__":
    root = tk.Tk()
    app = VerityAssistant(root)
    root.mainloop()