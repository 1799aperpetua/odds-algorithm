import customtkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x500")
        self.title("Mispriced Plays Finder")
        self.minsize(900, 400)

        # Create a 1x5 grid
        #self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight = 1)

        
        # Table to display today's picks
        self.table_space = customtkinter.CTkTextbox(master=self, bg_color="white")
        self.table_space.grid(row = 0, column = 2, columnspan = 7, rowspan = 10, padx = 20, pady = (20, 0), sticky = "nsew")

        # Header: API Key
        self.header_label = customtkinter.CTkLabel(master=self, text="Enter your API key below")
        self.header_label.grid(row = 0, column = 0, padx = 20, pady = (20, 0), sticky="ew")

        # Entry:  Field to enter your API key into
        self.api_entry = customtkinter.CTkEntry(master = self)
        self.api_entry.grid(row = 1, column = 0, padx = 10, pady = (10, 0))

        # Variable (string): Which sport would you like to query
        self.sport = customtkinter.StringVar()
        self.sport.set("baseball_mlb")

        # Buttons (radiobuttons): Sports
        self.mlb_button = customtkinter.CTkRadioButton(master = self, text = "MLB", variable = self.sport, value = "baseball_mlb")
        self.mlb_button.grid(row = 4, column = 0, padx = 20, pady = (20, 0))

        # Button:  Submit button
        self.submit_button = customtkinter.CTkButton(master = self, text = 'Submit', command = self.Submit)
        self.submit_button.grid(row = 3, column = 0, padx = 10, pady = (10, 0))
    
    def Submit(self):
        input_key = self.api_entry.get()
        sport = self.sport.get()

        print('Key:', input_key)
        print('Sport:', sport)

if __name__ == "__main__":
    app = App()
    app.mainloop()


