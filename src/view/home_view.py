import customtkinter
import pathlib
from PIL import ImageTk, Image
import webbrowser as wb


class HomeView(customtkinter.CTkFrame):
    def __init__(self, parent, main):
        super().__init__(parent)
        self.main = main

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Spacing
        self.grid_rowconfigure(1, weight=0)  # - Logo
        self.grid_rowconfigure(2, weight=0)  # - Note
        self.grid_rowconfigure(3, weight=0)  # - Buttons
        self.grid_rowconfigure(4, weight=0)  # - Buttons
        self.grid_rowconfigure(5, weight=1)  # Spacing

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        # Logo
        self.logo_path = pathlib.Path(__file__).parent.parent.parent.resolve()
        self.logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/documentation/wiki_images/logo.png").resize((433, 67)), Image.ANTIALIAS)
        self.label_logo = customtkinter.CTkLabel(self, image=self.logo)
        self.label_logo.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=15, pady=15)

        # Description label
        self.note = ("The universal OSRS color bot.\n Select a game in the left-side menu to begin.")
        self.label_note = customtkinter.CTkLabel(master=self,
                                                 text=self.note,
                                                 text_font=("Roboto", 14))
        self.label_note.bind('<Configure>', lambda e: self.label_note.configure(wraplength=self.label_note.winfo_width()-20))
        self.label_note.grid(row=2, column=0, columnspan=3, sticky="nwes", padx=15, pady=(0, 30))

        # Buttons
        IMG_SIZE = 24
        BTN_WIDTH, BTN_HEIGHT = (96, 64)
        DEFAULT_GRAY = ("gray50", "gray30")
        # -- Github
        self.github_logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/src/images/ui/github32_w.png").resize((IMG_SIZE, IMG_SIZE)), Image.LANCZOS)
        self.btn_github = customtkinter.CTkButton(master=self,
                                                  text="GitHub",
                                                  image=self.github_logo,
                                                  width=BTN_WIDTH,
                                                  height=BTN_HEIGHT,
                                                  corner_radius=15,
                                                  fg_color=DEFAULT_GRAY,
                                                  compound="top",
                                                  command=self.btn_github_clicked)
        self.btn_github.grid(row=3, column=0, padx=15, pady=(15, 0), sticky="e")

        # -- Feedback
        self.feedback_logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/src/images/ui/feedback_w.png").resize((IMG_SIZE, IMG_SIZE)), Image.LANCZOS)
        self.btn_feedback = customtkinter.CTkButton(master=self,
                                                    text="Feedback",
                                                    image=self.feedback_logo,
                                                    width=BTN_WIDTH,
                                                    height=BTN_HEIGHT,
                                                    corner_radius=15,
                                                    fg_color=DEFAULT_GRAY,
                                                    compound="top",
                                                    command=self.btn_feedback_clicked)
        self.btn_feedback.grid(row=3, column=1, padx=15, pady=(15, 0))

        # -- Bug Report
        self.bug_logo = ImageTk.PhotoImage(Image.open(f"{self.logo_path}/src/images/ui/bug-report_w.png").resize((IMG_SIZE, IMG_SIZE)), Image.LANCZOS)
        self.btn_feedback = customtkinter.CTkButton(master=self,
                                                    text="Report Bug",
                                                    image=self.bug_logo,
                                                    width=BTN_WIDTH,
                                                    height=BTN_HEIGHT,
                                                    corner_radius=15,
                                                    fg_color=DEFAULT_GRAY,
                                                    hover_color="#b36602",
                                                    compound="top",
                                                    command=self.btn_bug_report_clicked)
        self.btn_feedback.grid(row=3, column=2, padx=15, pady=(15, 0), sticky="w")

    def btn_github_clicked(self):
        wb.open_new_tab("https://github.com/kell90/OSRS-Bot-COLOR")

    def btn_feedback_clicked(self):
        wb.open_new_tab("https://github.com/kell90/OSRS-Bot-COLOR/discussions")

    def btn_bug_report_clicked(self):
        wb.open_new_tab("https://github.com/kell90/OSRS-Bot-COLOR/issues/new/choose")
