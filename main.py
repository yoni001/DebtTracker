from datetime import datetime
import json
import os
from os.path import join
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

# Make instances of kv classes
from kivy.lang import Builder

# To manipulate the frame
from kivy.clock import Clock
from kivy.factory import Factory

from kivy.uix.screenmanager import Screen
from kivy.properties import ListProperty


# Screens
class HomeScreen(Screen):
    pass


class HistoryScreen(Screen):
    pass


# Colored background for the rows of debts listed
class ColoredBoxLayout(BoxLayout):
    bg_color = ListProperty([0.1, 0.2, 0.3, 1])
    rad = 18


class DebtHolderApp(App):
    # Initialize the app
    def __init__(self, **kwargs):
        super(DebtHolderApp, self).__init__(**kwargs)
        self.next_id = 1
        self.debts = []
        # Join directory with app private directory,
        # that kivy provides. works for apk
        self.file_path = join(self.user_data_dir, "data.json")
        self.edit_id = None
        self.addPopup = None

    # Load data and refrsh when the app starts
    def on_start(self):
        self.load_data()
        self.refresh_list()
        # Create an instance of the class in kv file
        self.addPopup = Factory.AddDebtPopup()

    # Save data on local storage
    def save_data(self):
        with open(self.file_path, "w") as f:
            json.dump(self.debts, f, indent=2)

    # Load data from local storage
    def load_data(self):
        # Check if the file exists before loading
        if not os.path.exists(self.file_path):
            return

        try:
            # Load the data
            with open(self.file_path, "r") as f:
                self.debts = json.load(f)
        except json.JSONDecodeError:
            # hanfle corrupted or empty save file
            self.debts = []

        # Update the next id
        if self.debts:
            self.next_id = max(d["id"] for d in self.debts) + 1

    # When + is pressed
    def open_add_popup(self):
        # Open the popup
        self.addPopup.open()

    # Make the popup disappear first,
    # before doing logic
    def schedule_reset_popup(self, func):
        # Delay the logic and run on the next frame
        Clock.schedule_once(func, 0.2)

    # When add/edit popup is closed
    # .args because it takes two arguments
    def reset_add_popup(self, *args):
        # Empty the text inputs
        self.addPopup.ids.name_input.text = ""
        self.addPopup.ids.debt_input.text = ""
        self.addPopup.ids.debt_reason.text = ""

        # Return the text to add
        self.addPopup.ids.submit_button.text = "Add"
        self.edit_id = None
        # Change the label back
        self.addPopup.ids.add_popup_label.text = "Add a new debt owner."

    # Refresh list
    def refresh_list(self):
        container = self.root.get_screen("home").ids.list_container
        # Clear everything inside
        container.clear_widgets()

        # Total debt amount
        total = 0

        # Get index and values
        for i, d in enumerate(self.debts):
            total += d["debt"]

            if i % 2 == 0:
                bg_color = (0.3, 0.3, 0.9, 1)
            else:
                bg_color = (0.2, 0.2, 0.7, 1)

            # Row containing name|debt|edit|View History|delete
            rows = Factory.ColoredBoxLayout(
                size_hint_y = None,
                spacing="5dp",
                padding="5dp",
                bg_color=bg_color,
            )
            rows.bind(height=rows.setter("minimum_height"))

            # Add the name and debt
            labels_layout = BoxLayout()
            labels_layout.add_widget(Label(text=d["name"]))
            labels_layout.add_widget(
                Label(text=str(d["debt"]) + " Birr")
            )

            # Add edit and delete button
            btn_layout = BoxLayout(spacing="5dp")
            edit_btn = Factory.RoundedButton(
                text="[color=#90ff90]Edit[/color]",
                bg_color=(0.3, 0.7, 0.3, 0),
                size_hint_x = None,
                width = "40dp",
                markup=True,
            )
            # On press wants a callback,
            # lambda ensures that and the function will only be called when pressed
            edit_btn.bind(on_press=lambda _, i=d["id"]: self.edit_debt(i))

            delete_btn = Factory.RoundedButton(
                text="[color=#ff9090]Delete[/color]",
                bg_color=(0.7, 0.3, 0.3, 0),
                size_hint_x = None,
                width = "50dp",
                markup=True,
            )
            delete_btn.bind(on_press=lambda _, i=d["id"]: self.delete_debt(i))

            history_btn = Factory.RoundedButton(
                text="[color=#acaaff]View History[/color]", 
                bg_color=(0.3, 0.4, 0.7, 0),
                
                markup=True
            )
            history_btn.bind(on_press=lambda _, i=d["id"]: self.open_history_screen(i))

            btn_layout.add_widget(edit_btn)
            btn_layout.add_widget(history_btn)
            btn_layout.add_widget(delete_btn)

            rows.add_widget(labels_layout)
            rows.add_widget(btn_layout)
            # Add row in the main container
            container.add_widget(rows)

        # Change the total label in kv
        self.root.get_screen("home").ids.totalDebt.text = f"Total: {str(total)} Birr"

    # Edit debt
    def edit_debt(self, debt_id):
        self.edit_id = debt_id
        # Get the value using the debt_id
        debt_info = next(d for d in self.debts if d["id"] == debt_id)

        # Open the popup
        self.addPopup.open()

        # Change the label
        self.addPopup.ids.add_popup_label.text = (
            f"Edit {debt_info['name']}'s debt information."
        )
        # change the text input to show values
        self.addPopup.ids.name_input.text = debt_info["name"]
        self.addPopup.ids.debt_input.text = str(debt_info["debt"])
        # Change the submit text
        self.addPopup.ids.submit_button.text = "Save"

    # Open the history screen
    def open_history_screen(self, debt_id):
        self.current_debt = next(d for d in self.debts if d["id"] == debt_id)

        # switch screen
        self.root.current = "history"
        self.load_history()

    # Delete a give id's data
    def delete_debt(self, debt_id):
        self.debts = [d for d in self.debts if d["id"] != debt_id]
        self.save_data()
        self.refresh_list()

    # Load the history entries
    def load_history(self):
        container = self.root.get_screen("history").ids.history_container
        container.clear_widgets()
        num = 0

        current_debt = self.current_debt["debt"]
        self.root.get_screen("history").ids.current_label.text = (
            f"Current Debt: {current_debt} Birr"
        )

        for entry in reversed(self.current_debt.get("history", [])):
            text = f"Reason: {entry['reason']}\nDate added: {entry['timestamp']}"

            if num % 2 == 0:
                bg_color = (0.3, 0.3, 0.9, 1)
            else:
                bg_color = (0.2, 0.2, 0.7, 1)

            holder = Factory.ColoredBoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height="100dp",
                padding="5dp",
                bg_color=bg_color,
            )

            if entry["amount"] > 0:
                txt_color = "#33e66b"
            elif entry["amount"] < 0:
                txt_color = "#e63366"
            else:
                txt_color = "#ffffff"

            amount_label = Label(
                text=f"Amount: [color={txt_color}]{entry['amount']} Birr[/color]",
                markup=True,
                font_size="20sp",
                valign="center",
            )
            amount_label.bind(size=amount_label.setter("text_size"))

            text_label = Label(text=text, font_size="18sp", valign="center")
            text_label.bind(size=text_label.setter("text_size"))

            holder.add_widget(amount_label)
            holder.add_widget(text_label)

            container.add_widget(holder)
            num += 1

    # Add a new debt holder
    def add_debt(self):
        # Get values from text inputs
        name = self.addPopup.ids.name_input.text
        debt_text = self.addPopup.ids.debt_input.text
        reason = self.addPopup.ids.debt_reason.text

        right_num, op, left_num = None, None, None

        # Exist if the values are empty
        if not name or not debt_text or not reason:
            return

        # Separate to do operations
        parts = re.split(r"([+-])", debt_text)
        if len(parts) == 3:
            right_number, op, left_number = parts
            try:
                right_num = float(right_number)
                left_num = float(left_number)
            except ValueError:
                print("Can't two numbers change")
                return
        else:
            # Change string to float
            try:
                debt = float(debt_text)
            except ValueError:
                print("Can't change")
                return

        # Add a new value
        if not self.edit_id:
            # New debt to be added
            new_debt = {
                "id": self.next_id,
                "name": name,
                "debt": debt,
                "history": [
                    {
                        "amount": debt,
                        "reason": reason,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                ],
            }
            # Update next id
            self.next_id += 1
            # Add to dict
            self.debts.append(new_debt)
        else:  # Edit a value
            new_debt = None
            # Get the value using edit_id
            debt_info = next(d for d in self.debts if d["id"] == self.edit_id)

            # Do operation if needed
            if op == "+":
                new_debt = right_num + left_num
            elif op == "-":
                new_debt = right_num - left_num

            # New debt can be zero and still be taken
            final_debt = new_debt if new_debt is not None else debt

            # Update the value of the chosen debt
            changed_debt = final_debt - debt_info["debt"]

            debt_info["history"].append(
                {
                    "amount": changed_debt,
                    "reason": reason,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

            debt_info["name"] = name
            debt_info["debt"] = final_debt

        # Save data
        self.save_data()
        # Refresh the list shown
        self.refresh_list()

        # Close the popup
        self.addPopup.dismiss()


DebtHolderApp().run()
