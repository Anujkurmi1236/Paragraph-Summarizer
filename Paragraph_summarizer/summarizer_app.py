# summarizer_app.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import pyperclip
import re
from collections import Counter
import sys
import os
from PIL import Image, ImageDraw, ImageTk
import io

class TextSummarizer:
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'must', 'can', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'between', 'among', 'this',
            'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
            'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
            'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves'
        }

    def summarize(self, text, ratio=0.3):
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return text

        word_freq = self._calculate_word_frequency(sentences)
        sentence_scores = self._score_sentences(sentences, word_freq)
        num_sentences = max(1, int(len(sentences) * ratio))
        top_sentences = self._select_top_sentences(sentence_scores, num_sentences)

        return self._create_summary(top_sentences)

    def _split_sentences(self, text):
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_word_frequency(self, sentences):
        word_freq = Counter()
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            for word in words:
                if word not in self.stop_words and len(word) > 2:
                    word_freq[word] += 1
        return word_freq

    def _score_sentences(self, sentences, word_freq):
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence.lower())
            score = sum(word_freq[word] for word in words
                        if word not in self.stop_words and len(word) > 2)
            word_count = len([w for w in words if w not in self.stop_words and len(w) > 2])
            avg_score = score / max(word_count, 1)
            sentence_scores.append({
                'sentence': sentence,
                'score': avg_score,
                'position': i
            })
        return sentence_scores

    def _select_top_sentences(self, sentence_scores, num_sentences):
        sorted_sentences = sorted(sentence_scores, key=lambda x: x['score'], reverse=True)
        top_sentences = sorted_sentences[:num_sentences]
        top_sentences.sort(key=lambda x: x['position'])
        return top_sentences

    def _create_summary(self, selected_sentences):
        summary_parts = [s['sentence'] for s in selected_sentences]
        return '. '.join(summary_parts) + '.'


class FloatingIcon:
    def __init__(self, on_click_callback):
        self.on_click_callback = on_click_callback
        self.root = tk.Tk()
        self.root.title("Text Summarizer")

        # Create floating icon window
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-topmost', True)  # Always on top
        self.root.geometry("60x60+100+100")  # Size and position

        # Create icon
        self.create_icon()

        # Make draggable
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        self.root.bind('<Double-Button-1>', self.on_double_click)

        # Add right-click menu
        self.create_context_menu()

    def create_icon(self):
        # Create a simple icon using PIL
        img = Image.new('RGBA', (50, 50), (0, 150, 255, 200))
        draw = ImageDraw.Draw(img)

        # Draw a document-like icon
        draw.rectangle([10, 5, 40, 45], fill=(255, 255, 255, 255), outline=(0, 100, 200, 255), width=2)
        draw.line([15, 15, 35, 15], fill=(0, 100, 200, 255), width=2)
        draw.line([15, 20, 35, 20], fill=(0, 100, 200, 255), width=2)
        draw.line([15, 25, 30, 25], fill=(0, 100, 200, 255), width=2)

        # Add "S" for Summarizer
        draw.text((20, 30), "S", fill=(0, 100, 200, 255))

        # Convert to PhotoImage
        self.icon_photo = ImageTk.PhotoImage(img)

        # Create label with icon
        self.icon_label = tk.Label(self.root, image=self.icon_photo, bg='white')
        self.icon_label.pack(expand=True, fill='both')

        # Bind events to label too
        self.icon_label.bind('<Button-1>', self.start_drag)
        self.icon_label.bind('<B1-Motion>', self.drag)
        self.icon_label.bind('<ButtonRelease-1>', self.stop_drag)
        self.icon_label.bind('<Double-Button-1>', self.on_double_click)
        self.icon_label.bind('<Button-3>', self.show_context_menu)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open Summarizer", command=self.on_double_click)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.root.quit)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.root.geometry(f"60x60+{x}+{y}")

    def stop_drag(self, event):
        pass

    def on_double_click(self, event=None):
        self.on_click_callback()

    def run(self):
        self.root.mainloop()


class SummarizerWindow:
    def __init__(self):
        self.summarizer = TextSummarizer()
        self.window = None

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.window = tk.Toplevel()
        self.window.title("Text Summarizer")
        self.window.geometry("800x600")

        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Input section
        ttk.Label(main_frame, text="Input Text:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky="w",
                                                                                   pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
        self.input_text.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        control_frame.grid_columnconfigure(1, weight=1)

        # Summary ratio
        ttk.Label(control_frame, text="Summary Ratio:").grid(row=0, column=0, padx=(0, 10))

        self.ratio_var = tk.DoubleVar(value=0.3)
        ratio_scale = ttk.Scale(control_frame, from_=0.1, to=0.8, variable=self.ratio_var, orient="horizontal")
        ratio_scale.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        self.ratio_label = ttk.Label(control_frame, text="30%")
        self.ratio_label.grid(row=0, column=2, padx=(0, 10))

        def update_ratio_label(*args):
            self.ratio_label.config(text=f"{int(self.ratio_var.get() * 100)}%")

        self.ratio_var.trace('w', update_ratio_label)

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=3)

        ttk.Button(button_frame, text="Paste from Clipboard", command=self.paste_from_clipboard).pack(side="left",
                                                                                                      padx=(0, 5))
        ttk.Button(button_frame, text="Summarize", command=self.summarize_text).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(side="left")

        # Output section
        ttk.Label(main_frame, text="Summary:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky="w",
                                                                                pady=(10, 5))

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, sticky="nsew")
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Output buttons
        output_button_frame = ttk.Frame(output_frame)
        output_button_frame.grid(row=0, column=1, sticky="ns")

        ttk.Button(output_button_frame, text="Copy to\nClipboard", command=self.copy_to_clipboard).pack(pady=(0, 5))
        ttk.Button(output_button_frame, text="Save to\nFile", command=self.save_to_file).pack()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def paste_from_clipboard(self):
        try:
            clipboard_text = pyperclip.paste()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, clipboard_text)
            self.status_var.set("Text pasted from clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {str(e)}")

    def summarize_text(self):
        input_text = self.input_text.get(1.0, tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter some text to summarize")
            return

        self.status_var.set("Summarizing...")
        self.window.update()

        def summarize_thread():
            try:
                summary = self.summarizer.summarize(input_text, self.ratio_var.get())

                # Update UI in main thread
                self.window.after(0, lambda: self.display_summary(summary))
            except Exception as e:
                self.window.after(0, lambda: messagebox.showerror("Error", f"Summarization failed: {str(e)}"))
                self.window.after(0, lambda: self.status_var.set("Error occurred"))

        threading.Thread(target=summarize_thread, daemon=True).start()

    def display_summary(self, summary):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, summary)

        # Calculate statistics
        input_sentences = len(self.summarizer._split_sentences(self.input_text.get(1.0, tk.END)))
        output_sentences = len(self.summarizer._split_sentences(summary))

        self.status_var.set(f"Summary complete: {input_sentences} → {output_sentences} sentences")

    def copy_to_clipboard(self):
        summary = self.output_text.get(1.0, tk.END).strip()
        if summary:
            pyperclip.copy(summary)
            self.status_var.set("Summary copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No summary to copy")

    def save_to_file(self):
        summary = self.output_text.get(1.0, tk.END).strip()
        if not summary:
            messagebox.showwarning("Warning", "No summary to save")
            return

        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(summary)
                self.status_var.set(f"Summary saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Text cleared")


def main():
    summarizer_window = SummarizerWindow()

    def show_summarizer():
        summarizer_window.show()

    # Create and run floating icon
    floating_icon = FloatingIcon(show_summarizer)
    floating_icon.run()


if __name__ == "__main__":
    main()


