import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import chardet  # Library to detect file encoding

class TextCombinerApp:
    def __init__(self, master):
        self.master = master
        master.title("Text File Combiner")
        master.geometry("500x400")
        
        # UI Elements
        self.label = tk.Label(master, text="Select text files to combine:", font=("Arial", 12))
        self.label.pack(pady=10)

        self.select_button = tk.Button(master, text="Select Files", command=self.select_files, font=("Arial", 10))
        self.select_button.pack(pady=5)

        self.clear_button = tk.Button(master, text="Clear Files", command=self.clear_files, font=("Arial", 10))
        self.clear_button.pack(pady=5)

        self.file_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, width=60, height=10, font=("Arial", 10))
        self.file_listbox.pack(pady=10)

        self.combine_button = tk.Button(master, text="Combine Files", command=self.combine_files, font=("Arial", 10))
        self.combine_button.pack(pady=5)

        self.progress = ttk.Progressbar(master, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.output_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=8, width=60, font=("Arial", 10))
        self.output_area.pack(pady=10)

        self.file_list = []
        self.encoding_warnings = []  # List to store encoding warnings

    def select_files(self):
        files = filedialog.askopenfilenames(title="Select Text Files", filetypes=[("Text Files", "*.txt")])
        if files:
            self.file_list = list(files)
            self.update_file_listbox()
            self.label.config(text=f"Selected {len(self.file_list)} files.")

    def clear_files(self):
        self.file_list = []
        self.update_file_listbox()
        self.label.config(text="Select text files to combine:")
        self.encoding_warnings.clear()  # Clear any previous warnings

    def update_file_listbox(self):
        self.file_listbox.delete(0, tk.END)  # Clear the listbox
        for file in self.file_list:
            self.file_listbox.insert(tk.END, file)

    def combine_files(self):
        if not self.file_list:
            messagebox.showwarning("No Files Selected", "Please select text files to combine.")
            return

        # Automatically create a new output filename based on the first selected file
        output_directory = os.path.dirname(self.file_list[0])
        base_filename = f"combined_{os.path.basename(self.file_list[0])}"
        self.output_file = os.path.join(output_directory, base_filename)

        self.progress['value'] = 0
        self.progress['maximum'] = len(self.file_list)

        try:
            with open(self.output_file, 'w', encoding='utf-8') as outfile:
                for idx, fname in enumerate(self.file_list):
                    encoding = self.detect_encoding(fname)
                    try:
                        with open(fname, 'r', encoding=encoding) as infile:
                            outfile.write(infile.read() + "\n")
                    except UnicodeDecodeError:
                        # Log the warning instead of showing a popup
                        self.encoding_warnings.append(f"Failed to decode {fname} with {encoding}. Using ISO-8859-1 instead.")
                        with open(fname, 'r', encoding='ISO-8859-1') as infile:
                            outfile.write(infile.read() + "\n")
                    
                    self.progress['value'] += 1
                    self.master.update_idletasks()  # Update the progress bar

            # Delete the selected files after combining
            for fname in self.file_list:
                os.remove(fname)

            messagebox.showinfo("Success", f"Files combined successfully into:\n{self.output_file}")

            # Display encoding warnings if any
            if self.encoding_warnings:
                warnings_message = "\n".join(self.encoding_warnings)
                messagebox.showinfo("Warnings", f"Warnings encountered during processing:\n{warnings_message}")

            self.display_combined_content()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def detect_encoding(self, file_path):
        """Detect the encoding of a given file."""
        with open(file_path, 'rb') as file:
            rawdata = file.read(10000)  # Read first 10,000 bytes for detection
        result = chardet.detect(rawdata)
        return result['encoding']

    def display_combined_content(self):
        """Display the content of the combined file in the output area."""
        with open(self.output_file, 'r', encoding='utf-8') as file:
            content = file.read()
            self.output_area.delete(1.0, tk.END)  # Clear previous content
            self.output_area.insert(tk.END, content)  # Display the new content

if __name__ == "__main__":
    root = tk.Tk()
    app = TextCombinerApp(root)
    root.mainloop()
