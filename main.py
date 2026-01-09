import json
import os
from os.path import join
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
# Make instances of kv classes
from kivy.lang import Builder
# To manipulate the frame
from kivy.clock import Clock

class MyApp(App):
	# Initialize the app
	def __init__(self, **kwargs):
		super(MyApp, self).__init__(**kwargs)
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
		# Create an instance for adding a new debt
		self.addPopup = Builder.load_string("AddDebtPopup:")
   
   
	# Save data on local storage
	def save_data(self):
		with open(self.file_path, "w") as f:
			json.dump(self.debts, f, indent = 2)
   	
   	
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
			#hanfle corrupted or empty save file
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
	def schedule_reset_popup(self,func):
		# Delay the logic and run on the next frame
		Clock.schedule_once(func, 0.2)
   
   
	# When add/edit popup is closed
	# .args because it takes two arguments
	def reset_add_popup(self, *args):
		# Empty the text inputs
		self.addPopup.ids.name_input.text = ""
		self.addPopup.ids.debt_input.text = ""

		# Return the text to add
		self.addPopup.ids.submit_button.text = "Add"
		self.edit_id = None
		# Change the label back
		self.addPopup.ids.add_popup_label.text = "Add a new debt owner."
   
   
	# Refresh list
	def refresh_list(self):
		container = self.root.ids.list_container
		# Clear everything inside
		container.clear_widgets()

		# Total debt amount
		total = 0

		# Get index and values
		for i, d in enumerate(self.debts):
			total += d["debt"]

			# Row containing name|debt|edit|delete
			rows = BoxLayout(
				size_hint_y = None, 
				height = 80,
				spacing = 5
			)

			# Add the name and debt
			labels_layout = BoxLayout()
			labels_layout.add_widget(
				Label(text=str(i+1), size_hint_x=None)
			)
			labels_layout.add_widget(
				Label(text=d["name"], size_hint_x = .2)
			)
			labels_layout.add_widget(
				Label(text=str(d["debt"])+" Birr", size_hint_x = .2)
			)

			# Add edit and delete button
			btn_layout = BoxLayout(
				size_hint_x = .5,
				spacing = 20,
				width = 150
			)
			edit_btn = Button(
				text="Edit", 
				size_hint_x = None,
				width = 120
			)
			delete_btn = Button(
				text = "Delete",
				size_hint_x = None,
				width = 180
			)
			# On press wants a callbacl, 
			# lambda ensures that and the function will only be called when pressed 
			delete_btn.bind(on_press=lambda _, i=d["id"]: self.delete_debt(i))
			edit_btn.bind(on_press=lambda _, i=d["id"]: self.edit_debt(i))

			btn_layout.add_widget(edit_btn)
			btn_layout.add_widget(delete_btn)

			rows.add_widget(labels_layout)
			rows.add_widget(btn_layout)
			# Add row in the main container
			container.add_widget(rows)
   		
		# Total debts label
		total_debts = Label(text=f"Total: {total} Birr", size_hint_y=None, height= '30dp', halign="left", valign="middle")
		# Bind to make align work
		total_debts.bind(size=total_debts.setter("text_size"))
		container.add_widget(total_debts)
   		
   		
	# Edit debt
	def edit_debt(self, debt_id):
		self.edit_id = debt_id
		# Get the value using the debt_id
		debt_info = next(d for d in self.debts if d["id"] == debt_id)

		# Open the popup
		self.addPopup.open()

		# Change the label
		self.addPopup.ids.add_popup_label.text = f"Edit {debt_info['name']}'s debt information."
		# change the text input to show values
		self.addPopup.ids.name_input.text = debt_info["name"]
		self.addPopup.ids.debt_input.text = str(debt_info["debt"])
		# Change the submit text
		self.addPopup.ids.submit_button.text = "Save"
   
   
	# Delete a give id's data
	def delete_debt(self, debt_id):
		self.debts = [d for d in self.debts if d["id"]!=debt_id]
		self.save_data()
		self.refresh_list()
   
   
	# Add a new debt holder
	def add_debt(self):
		# Get values from text inputs
		name = self.addPopup.ids.name_input.text
		debt_text = self.addPopup.ids.debt_input.text
   	
		# Exist if the values are empty
		if not name or not debt_text:
			return
		
		# Change string to float
		try:
			debt = float(debt_text)
		except ValueError:
			return

		# Add a new value
		if not self.edit_id:
			# New debt to be added
			new_debt = {
				"id": self.next_id,
				"name": name,
				"debt": debt
				}
				# Update next id
			self.next_id += 1
				# Add to dict
			self.debts.append(new_debt)
		else: # Edit a value
			# Get the value using edit_id
			debt_info = next(d for d in self.debts if d["id"] == self.edit_id)
			# Update the value of the chosen debt
			debt_info["name"] = name
			debt_info["debt"] = debt
			
		# Save data
		self.save_data()
		# Refresh the list shown
		self.refresh_list()
		
		# Close the popup
		self.addPopup.dismiss()

MyApp().run()
