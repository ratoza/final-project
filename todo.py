import kivy
import copy
import firebase_admin
from firebase_admin import credentials,firestore
kivy.require("1.10.0")
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty,BooleanProperty,ListProperty,ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

from kivy.uix.recycleview.views import RecycleDataViewBehavior,RecycleDataAdapter
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout


class TodoCard:
	def __init__(self):
		self.doc_ref = None # Firebase document reference
		self.list_of_todos = [] # loaded list of todos from db
		self.database_connection() # Calling database_connection function
		self.selected_todo = None # the selected todo
		self.pop_action = None # type of pop up 'create' or 'edit'
		self.index = None # index of the selected todo from list_of_todos list
		# Predefined color array
		self.colors = {
			"blue": [0,0,1,1], 
			"red": [1,0,0,1], 
			"white": [1,1,1,1]
		}

	def database_connection(self):
		cred = credentials.Certificate("ServerAccountKey.json")
		firebase_admin.initialize_app(cred)
		db = firestore.client()
		self.doc_ref = db.collection(u'Todo').document(u'todo_list')
		try:
			doc = self.doc_ref.get()
			if doc.to_dict() is None:
				self.doc_ref.set({
				    u'data': [
				    	{u'time': u'11:20 PM', u'date': u'18/11/2019', u'title': u'Doctor appointment', u'color': u'red',u'done': False},
				    	{u'date': u'19/11/2019', u'title': u'Final math', u'color': u'blue', u'time': u'2:00 PM',u'done': False},
				    	{u'color': u'red', u'time': u'11:00 AM', u'date': u'20/11/2019', u'title': u'final physics',u'done': False},
				    	{u'color': u'red', u'time': u'11:00 AM', u'date': u'13/11/2018', u'title': u'final physics',u'done': True}

				    ]
				})
				doc = self.doc_ref.get()

			data_from_db = doc.to_dict()
			self.list_of_todos = data_from_db['data']
		except google.cloud.exceptions.NotFound:
			print(u'No such document!')

	def get_todo_list(self):
		res = []
		for todo in self.list_of_todos:
			if not todo['done']:
				res.append(todo)
		self.list_of_todos = res
		return res

	def set_todo_selected(self,selected,index):
		self.selected_todo = selected
		self.index = index

	def update_database(self):
		self.doc_ref.set({
		    u'data': self.list_of_todos
		})

	def create_todo(self,new_todo):
		self.list_of_todos.append(new_todo)
		self.update_database()
		return self.list_of_todos

	def edit_todo(self,edit_todo):
		if self.selected_todo is not None:
			self.list_of_todos[self.index] = edit_todo
			self.update_database()
			return self.list_of_todos
		return self.list_of_todos

	def delete_todo(self,list_of_todos):
		if self.selected_todo is not None:
			del list_of_todos[self.index]
			self.list_of_todos = list_of_todos
			self.update_database()
			return (True,list_of_todos)
		return (False,list_of_todos)

	def refresh_data(self,new_data):
		root = App.get_running_app().root
		root.ids.todo_grid_id.data = todo.get_todo_list()
		root.ids.todo_grid_id.refresh_from_data()

class CustomDropDown(BoxLayout):
    pass

class AlertPopup(Popup):
	title = StringProperty()
	message = StringProperty()

class MainPopup(Popup):
    """Popup for adding asset"""
    title_todo = ObjectProperty()

    date_todo_d = ObjectProperty() # day
    date_todo_m = ObjectProperty() # month
    date_todo_y = ObjectProperty() # year

    time_todo_h = ObjectProperty() # hours
    time_todo_m = ObjectProperty() # minutes
    time_todo_a = ObjectProperty() # AM || PM

    done_todo = ObjectProperty()
    color_red_todo = ObjectProperty()
    color_blue_todo = ObjectProperty()

    wrapped_button = ObjectProperty()
    title_pop_up = StringProperty()


    def __init__(self, *args, **kwargs):
    	super(MainPopup, self).__init__(*args, **kwargs)
    	self.title_pop_up = "Create Todo"
    	self.time_todo_a.text = 'AM'
    	self.done_todo.active = False
    	self.color_red_todo.active = False
    	self.color_blue_todo.active = False

    def pick_color(self,color):
    	if color == 'red':
    		self.color_red_todo.active = True
    		self.color_blue_todo.active = False
    	else:
    		self.color_red_todo.active = False
    		self.color_blue_todo.active = True

    def open(self, correct,type_action,todo_selected):
    	if(type_action == 'edit' and todo.selected_todo is not None):
    		time = todo_selected['time'].split(" ")
    		date = todo_selected['date'].split("/")
    		hour_min = time[0].split(":")
    		self.title_pop_up = "Edit Todo"
    		self.title_todo.text = todo_selected['title']
    		
    		self.date_todo_d.text = date[0]
    		self.date_todo_m.text = date[1]
    		self.date_todo_y.text = date[2]

    		self.time_todo_h.text = hour_min[0]
    		self.time_todo_m.text = hour_min[1]
    		self.time_todo_a.text = time[1]
    		self.pick_color(todo_selected['color'])

    		self.done_todo.active = todo_selected['done']
    	else:
    		self.title_todo.text = ''
    		
    		self.date_todo_d.text = ''
    		self.date_todo_m.text = ''
    		self.date_todo_y.text = ''
    		
    		self.time_todo_h.text = ''
    		self.time_todo_m.text = ''
    		self.time_todo_a.text = 'AM'
    		
    		self.color_red_todo.active = False
    		self.color_blue_todo.active = False
    		self.done_todo.active = False

    	super(MainPopup, self).open(correct)


    def save_todo(self):
        # Make sure no input is empty
        if self.title_todo.text.strip() and self.date_todo_d.text.strip()\
        	and self.date_todo_m.text.strip() and self.date_todo_y.text.strip()\
        	and self.time_todo_h.text.strip() and self.time_todo_m.text.strip()\
        	and self.time_todo_a.text.strip():
	        
	        time = self.time_todo_h.text.strip() + ":"+ self.time_todo_m.text.strip() +" "+self.time_todo_a.text.strip()
	        date = self.date_todo_d.text.strip()+"/"+self.date_todo_m.text.strip()+"/"+self.date_todo_y.text.strip()
	        color = 'blue'
	        if self.color_red_todo.active and not self.color_blue_todo.active:
	        	color = 'red'

	        data = {
	        'title': self.title_todo.text.strip(),
	        'time': time,
	        'date': date,
	        'color': color,
	        'done': self.done_todo.active
	        }
	        print(data)

	        list_of_todos = todo.list_of_todos

	        if(todo.pop_action == 'create'):
	        	list_of_todos = todo.create_todo(data)
	        	alert_popup = AlertPopup()
	        	alert_popup.title = 'Success'
	        	alert_popup.message = "You have created a new todo card!"
		        alert_popup.open()
	        else:
	        	list_of_todos = todo.edit_todo(data)
	        	alert_popup = AlertPopup()
	        	alert_popup.title = 'Success'
	        	alert_popup.message = "You have edit this todo card!"
		        alert_popup.open()
	        
	        todo.refresh_data(todo.get_todo_list())
	        self.dismiss()

        else:
        	alert_popup = AlertPopup()
        	alert_popup.title = 'Alert!!'
        	alert_popup.message = "Please enter the required fields before saving"
        	alert_popup.open()


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view. '''

class TodoCardView(RecycleDataViewBehavior, Label):
	index = None
	selected = BooleanProperty(False)
	selectable = BooleanProperty(True)
	color_label = ListProperty()
	
	def __init__(self, **kwargs):
		super(TodoCardView,self).__init__(**kwargs)

	def refresh_view_attrs(self, rv, index, data):
		self.index = index
		color = todo.colors

		self.color_label = color[data["color"]]
		date = data["date"].split("/")
		date_ref = {
			1: 'Jan', 2: 'Feb', 3: 'Mar',
			4: 'Apr', 5: 'May', 6: 'Jun',
			7: 'Jul', 8: 'Aug', 9: 'Sep',
			10: 'Oct', 11: 'Nov', 12: 'Dec'
		}
		date_str = date_ref[int(date[1])] + ", "+date[0] + " "+ date[2]
		text = "Title: "+ data["title"]+" \nDate: "+ date_str + " \nTime: "+ data["time"]
		data = {"text": text, "color": color["white"]}
		return super(TodoCardView, self).refresh_view_attrs(rv, index, data)

	def on_touch_down(self, touch):
		if super(TodoCardView, self).on_touch_down(touch):
		    return True
		if self.collide_point(*touch.pos) and self.selectable:
		    return self.parent.select_with_touch(self.index, touch)

	def apply_selection(self, rv, index, is_selected):
	    self.selected = is_selected
	    if is_selected:
	    	todo.set_todo_selected(rv.data[index], index)


class MainScreen(GridLayout):

	def __init__(self, **kwargs):
		super(MainScreen,self).__init__(**kwargs)
		self.todo_grid = TodoGrid()
		self.create_popup = MainPopup()

	def action_btn_press(self, btn):
		if btn == 'create':
			todo.pop_action = 'create'
			self.create_popup.open(True,btn,{})
		elif btn == 'edit':
			todo.pop_action = 'edit'
			self.create_popup.open(True,btn,todo.selected_todo)
		elif btn == 'remove':
			self.todo_grid.delete_data(todo.list_of_todos)
			
class TodoGrid(RecycleView):
	data = ListProperty()
	def __init__(self, **kwargs):
		super(TodoGrid, self).__init__(**kwargs)
		self.data = todo.get_todo_list()

	def delete_data(self,data):
		(validation,new_data) = todo.delete_todo(data)
		if not validation:
			alert_popup = AlertPopup()
			alert_popup.title = 'Alert!!'
			alert_popup.message = "Please select a card before deleting any"
			alert_popup.open()
		else:
			todo.refresh_data(new_data)


class TodoApp(App):
	def __init__(self):
		super().__init__()
		title = "Todo App"

	def build(self):
		self.main_screen = MainScreen()
		return self.main_screen

if __name__ == '__main__':
	todo = TodoCard()
	app = TodoApp()
	app.run()