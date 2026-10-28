import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator, MyMemoryTranslator
from deep_translator.exceptions import TooManyRequests

LANGUAGES = {
    "Auto Detect": "auto", "English": "en", "Bengali": "bn", "Hindi": "hi",
    "Spanish": "es", "French": "fr", "German": "de", "Italian": "it",
    "Portuguese": "pt", "Russian": "ru", "Japanese": "ja", "Korean": "ko",
    "Chinese (Simplified)": "zh-CN", "Arabic": "ar", "Urdu": "ur",
    "Nepali": "ne", "Tamil": "ta", "Telugu": "te", "Marathi": "mr",
}

class TranslationApp:
    def __init__(self, root):
        self.root = root
        root.title("CodeAlpha Language Translation Tool")
        root.geometry("820x620")
        root.minsize(680, 520)
        self.source_var = tk.StringVar(value="Auto Detect")
        self.target_var = tk.StringVar(value="Bengali")
        self.status_var = tk.StringVar(value="Ready")
        self.build_ui()

    def build_ui(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Language Translation Tool",
                  font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Enter text, choose languages, and click Translate.").pack(
            anchor="w", pady=(4, 14))
        row = ttk.Frame(outer)
        row.pack(fill="x", pady=(0, 10))
        ttk.Label(row, text="From:").pack(side="left")
        names = list(LANGUAGES.keys())
        ttk.Combobox(row, textvariable=self.source_var, values=names,
                     state="readonly", width=22).pack(side="left", padx=(6, 12))
        ttk.Button(row, text="Swap languages", command=self.swap_languages).pack(
            side="left", padx=(0, 12))
        ttk.Label(row, text="To:").pack(side="left")
        targets = [n for n in names if n != "Auto Detect"]
        ttk.Combobox(row, textvariable=self.target_var, values=targets,
                     state="readonly", width=22).pack(side="left", padx=6)
        ttk.Label(outer, text="Text to translate:").pack(anchor="w")
        self.input_text = tk.Text(outer, height=8, wrap="word", font=("Arial", 11))
        self.input_text.pack(fill="both", expand=True, pady=(5, 12))
        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(0, 12))
        self.translate_button = ttk.Button(buttons, text="Translate", command=self.translate_text)
        self.translate_button.pack(side="left")
        ttk.Button(buttons, text="Clear", command=self.clear_text).pack(side="left", padx=8)
        ttk.Label(outer, text="Translation:").pack(anchor="w")
        self.output_text = tk.Text(outer, height=8, wrap="word", font=("Arial", 11), state="disabled")
        self.output_text.pack(fill="both", expand=True, pady=(5, 8))
        bottom = ttk.Frame(outer)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Copy translation", command=self.copy_translation).pack(side="left")
        ttk.Label(bottom, textvariable=self.status_var).pack(side="right")

    def set_output(self, value):
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", value)
        self.output_text.configure(state="disabled")

    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("No text", "Please enter some text to translate.")
            return
        source = LANGUAGES[self.source_var.get()]
        target = LANGUAGES[self.target_var.get()]
        if source == target:
            messagebox.showinfo("Same language", "Please choose two different languages.")
            return
        self.translate_button.configure(state="disabled")
        self.status_var.set("Translating...")
        self.root.update_idletasks()
        try:
            try:
                result = GoogleTranslator(source=source, target=target).translate(text)
            except TooManyRequests:
                if source == "auto":
                    raise RuntimeError(
                        "Google's free service is limiting requests. Select the source "
                        "language manually (for example, English) and try again."
                    )
                self.status_var.set("Trying backup service...")
                self.root.update_idletasks()
                result = MyMemoryTranslator(source=source, target=target).translate(text)
            if not result:
                raise RuntimeError("The translation service returned an empty result.")
            self.set_output(result)
            self.status_var.set("Translation complete")
        except TooManyRequests:
            self.set_output("")
            self.status_var.set("Service limit reached")
            messagebox.showerror(
                "Translation service limit",
                "The translation service is temporarily limiting requests. "
                "Wait a while and try again; avoid repeated clicks."
            )
        except Exception as error:
            self.set_output("")
            self.status_var.set("Translation failed")
            messagebox.showerror(
                "Translation error",
                "Could not translate the text. Check internet, choose a source language "
                "manually if Auto Detect is selected, and try later.\n\n"
                f"Technical detail: {error}"
            )
        finally:
            self.translate_button.configure(state="normal")

    def swap_languages(self):
        source_name, target_name = self.source_var.get(), self.target_var.get()
        if source_name == "Auto Detect":
            messagebox.showinfo("Choose a source language", "Select a source language before swapping.")
            return
        self.source_var.set(target_name)
        self.target_var.set(source_name)
        output = self.output_text.get("1.0", "end").strip()
        if output:
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", output)
            self.set_output("")

    def clear_text(self):
        self.input_text.delete("1.0", "end")
        self.set_output("")
        self.status_var.set("Ready")

    def copy_translation(self):
        output = self.output_text.get("1.0", "end").strip()
        if not output:
            messagebox.showinfo("Nothing to copy", "Translate some text first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(output)
        self.status_var.set("Translation copied")

if __name__ == "__main__":
    root = tk.Tk()
    TranslationApp(root)
    root.mainloop()
