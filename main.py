import customtkinter
from script import QueryMispricedPlays

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1000x500")
        self.title("Mispriced Plays Finder")
        self.minsize(750, 600)

        self.instructions = customtkinter.CTkLabel(master = self, text="1. Create an account on https://the-odds-api.com/\n2. Copy your API key and paste it below\n3. Select your desired sport and press Submit\n\nThe program looks for price discrepancies across sportsbooks and groups them based on their value\nFormat: Sportsbook Team Price (Amount of value)")
        self.instructions.pack(padx = 10, pady = 10)

        # Header: API Key
        self.header_label = customtkinter.CTkLabel(master=self, text="Enter your API key below")
        self.header_label.pack(padx = 10, pady = 10)

        # Entry:  Field to enter your API key into
        self.api_entry = customtkinter.CTkEntry(master = self)
        self.api_entry.pack(padx = 10, pady = 10)

        # Variable (string): Which sport would you like to query
        self.sport = customtkinter.StringVar()
        self.sport.set("baseball_mlb")

        # Buttons (radiobuttons): Sports
        self.mlb_button = customtkinter.CTkRadioButton(master = self, text = "MLB", variable = self.sport, value = "baseball_mlb")
        self.mlb_button.pack(padx = 10, pady = 10)

        # Button:  Submit button
        self.submit_button = customtkinter.CTkButton(master = self, text = 'Submit', command = self.Submit)
        self.submit_button.pack(padx = 10, pady = 10)

        # Textbox:  Displays results
        self.table_space = customtkinter.CTkTextbox(master=self, bg_color="white", height = 200, width = 500)
        self.table_space.pack(padx = 10, pady = 10)
    
    def Submit(self):
        input_key = self.api_entry.get()
        sport = self.sport.get()

        mispricedPlays = QueryMispricedPlays(input_key, sport)
        self.table_space.insert('1.0', text=mispricedPlays)

if __name__ == "__main__":
    app = App()
    app.mainloop()


