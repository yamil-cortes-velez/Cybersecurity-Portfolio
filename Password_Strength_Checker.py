import tkinter as tk
import string

# Setup tk Window
root = tk.Tk()
root.title("Password Checker")
root.geometry("700x500")
root.configure(bg="black")

#Author Info
Yamil_Label = tk.Label(
    root,
    text = "Created By: Yamil Cortes Velez | 3/27/2026",
    fg = "White",
    bg = "black"
)
Yamil_Label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

# Define Characters
UppercaseCount = 0
LowercaseCount = 0
Specialcharacter = 0
PersonalInfo = False
Length = False
Counter = 0
SpecialChars = set(string.punctuation)

# Pre Define Requirements
Requirements = tk.Label(
    root,
    text="Requirements:\n\nLength: 12 to 17 characters\nSpecial Characters: 1 Minimum\nUppercase: 1 Minimum\nLowercase: 1 Minimum\nPersonal Info: None",
    foreground="white",
    background="black",
    width=50,
    height=10,
    justify="left"
)
Requirements.pack(pady=20)

# Name label and entry
NameLabel = tk.Label(
    root,
    text="What's your first and last name?",
    fg="white",
    bg="black"
)
NameLabel.pack()

NameEntry = tk.Entry(root, width=40)
NameEntry.pack(pady=5)

# Password label and entry
PassLabel = tk.Label(
    root,
    text="Insert Password",
    fg="white",
    bg="black"
)
PassLabel.pack()

PassEntry = tk.Entry(root, width=40, show="*")
PassEntry.pack(pady=5)

# Output label
ResultLabel = tk.Label(
    root,
    text="",
    fg="yellow",
    bg="black"
)
ResultLabel.pack(pady=20)

# Verification Process
def Verification():
    global UppercaseCount
    global LowercaseCount
    global Specialcharacter
    global PersonalInfo
    global Length
    global Counter

    # Reset values every time button is clicked
    UppercaseCount = 0
    LowercaseCount = 0
    Specialcharacter = 0
    PersonalInfo = False
    Length = False
    Counter = 0

    # Get Name and store First and Last Names
    UserName = NameEntry.get()
    FullName = UserName.split()

    if len(FullName) < 2:
        ResultLabel.config(text="Please enter both first and last name")
        return

    FirstName = FullName[0]
    LastName = FullName[1]

    # Get Password
    UserPass = PassEntry.get()

    # Count password length
    Counter = len(UserPass)

    # Check each character in password
    for char in UserPass:
        if char.isupper():
            UppercaseCount += 1
        elif char.islower():
            LowercaseCount += 1
        elif char in SpecialChars:
            Specialcharacter += 1

    # Check for personal info in password
    if FirstName.lower() in UserPass.lower() or LastName.lower() in UserPass.lower():
        PersonalInfo = True

    # Check password length
    if Counter >= 12 and Counter <= 17:
        Length = True
    else:
        Length = False

    # Confirm Password Strength
    if PersonalInfo:
        ResultLabel.config(text="Please Remove Personal Information and try again")
    elif not Length:
        ResultLabel.config(text="Password must be 12 to 17 characters")
    elif UppercaseCount >= 1 and LowercaseCount >= 1 and Specialcharacter >= 1:
        ResultLabel.config(text="Strong Password")
    else:
        if UppercaseCount < 1:
            ResultLabel.config(text="Try adding an Uppercase letter")
        elif LowercaseCount < 1:
            ResultLabel.config(text="Try adding a Lowercase letter")
        elif Specialcharacter < 1:
            ResultLabel.config(text="Please just throw 1 special character in there")

# Button
Button = tk.Button(
    root,
    text="Check",
    width=25,
    height=2,
    bg="blue",
    fg="yellow",
    command=Verification
)
Button.pack(pady=10)

root.mainloop()