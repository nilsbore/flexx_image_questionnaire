#!/usr/bin/python3

from flexx import flx, event, config
from tornado.web import StaticFileHandler
import string
import random
import json

config.hostname = "0.0.0.0" # maybe use socket.gethostname()
config.port = 8097

dirname = "/home/nbore/Installs/flexx_image_questionnaire"

# The program will look for these folders and present the lists as options
choices = {"1": ["q.png", "1.png", "2.png"],
           "2": ["q.png", "1.png", "2.png", "3.png"],
           "3": ["q.png", "1.png", "2.png"],
           "4": ["q.png", "1.png", "2.png", "3.png"]}

# Make use of Tornado's static file handler
tornado_app = flx.create_server().app
tornado_app.add_handlers(r".*", [
        (r"/images/(.*)", StaticFileHandler, {"path": dirname}),
            ])

class ImageChooser(flx.Widget):

    CSS = """
        .flx-Button {
            background: #9d9;
        }
        .flx-LineEdit {
            border: 2px solid #9d9;
        }
        .flx-GroupWidget {
            border: 2px solid #9d9;
        }
        """

    @event.reaction('pointer_click')
    def radio_clicked(self, *events):
        self.choice_done = True
        self.parent.parent.parent.parent.parent.parent.check_choices()

    def init(self, choicedir, choices):

        self.choicedir = choicedir # "1"
        self.choices = choices #choices["1"]
        self.choice_done = False

        with flx.GroupWidget(title="Which sidescan waterfall image looks most realistic?"):
            with flx.VBox():
                with flx.HFix():
                    self.ims = []
                    for c in self.choices[1:]:
                        with flx.VFix():
                            self.ims.append(flx.ImageWidget(stretch=False, source="/images/"+self.choicedir+"/"+c, minsize=(512., 512.)))

                with flx.HFix() as option_form:
                    self.rs = [flx.RadioButton(text=str(i)) for i in range(1, len(self.choices))]


class FolderChooser(flx.Widget):

    CSS = """
        .flx-Button {
            background: #9d9;
        }
        .flx-LineEdit {
            border: 2px solid #9d9;
        }
        .flx-GroupWidget {
            border: 2px solid #9d9;
        }
        """

    def init(self, choicedir, choices):

        self.choicedir = choicedir
        self.choices = choices
        
        with flx.VBox():
            flx.Widget(flex=1)  # Add a spacer

            with flx.HBox():

                with flx.GroupWidget(title="Given this bathymetry and vehicle track..."):
                    with flx.VBox():
                        self.i0 = flx.ImageWidget(stretch=False, source="/images/bathy.png")
                self.im_chooser = ImageChooser(choicedir, choices)
            flx.Widget(flex=1)  # Add a spacer

class UserDetails(flx.Widget):

    CSS = """
        .flx-Button {
            background: #9d9;
        }
        .flx-LineEdit {
            border: 2px solid #9d9;
        }
        .flx-GroupWidget {
            border: 2px solid #9d9;
        }
        """

    def init(self):

        with flx.HFix():
            flx.Widget(flex=1)  # Add a spacer
            with flx.FormLayout(flex=1) as self.form:
                flx.Widget(flex=1)  # Add a spacer
                self.name = flx.LineEdit(title='Name:', text='', maxsize=(600, 0))
                self.affiliation = flx.LineEdit(title='Affiliation:', text='', maxsize=(600, 0))
                with flx.HBox():
                    flx.Label(text="Familiarity with sidescan (0-10):")
                    self.familiarity = self.tension = flx.Slider(min=0, max=10, value=5,
                                                                 text=lambda: 'Familiarity: {value}', flex=1)
                flx.Label(text='When done, click the "Next" button')
                flx.Widget(flex=1)  # Add a spacer
            flx.Widget(flex=1)  # Add a spacer

class DoneScreen(flx.Widget):

    CSS = """
        .flx-Button {
            background: #9d9;
        }
        .flx-LineEdit {
            border: 2px solid #9d9;
        }
        .flx-GroupWidget {
            border: 2px solid #9d9;
        }
        """

    def init(self):

        self.thank_you = flx.Label(text="Submitted! Thank you for filling out the questionnaire!")


class Questionnaire(flx.Widget):

    CSS = """
        .flx-Button {
            background: #9d9;
        }
        .flx-LineEdit {
            border: 2px solid #9d9;
        }
        .flx-GroupWidget {
            border: 2px solid #9d9;
        }
        """

    def check_choices(self):

        for q in self.questions[1:]:
            if not q.im_chooser.choice_done:
                return

        self.submit.set_disabled(False)
        self.submit.apply_style("background: #9d9;")

    @event.reaction('next.pointer_down')
    def next_clicked(self, *events):
        if self.current_question < len(self.questions)-1:
            self.current_question += 1
            self.stack.set_current(self.questions[self.current_question])
            self.t1.set_text("Question " + str(self.current_question+1) + "/" + str(len(self.questions)))

    @event.reaction('previous.pointer_down')
    def previous_clicked(self, *events):
        if self.current_question > 0:
            self.current_question -= 1
            self.stack.set_current(self.questions[self.current_question])
            self.t1.set_text("Question " + str(self.current_question+1) + "/" + str(len(self.questions)))

    @event.reaction('submit.pointer_down')
    def submit_clicked(self, *events):
        
        filled_data = {}

        user_questions = self.questions[0]
        filled_data["name"] = user_questions.name.text
        filled_data["affiliation"] = user_questions.affiliation.text
        filled_data["sidescan_familiarity"] = user_questions.familiarity.value

        for q in self.questions[1:]:
            #data[q.choicedir] = [
            try:
                ind = map(lambda r: r.checked, q.im_chooser.rs).index(True)
                filled_data[q.choicedir] = q.choices[1+ind]
            except ValueError:
                filled_data[q.choicedir] = "None"
                print("Could not find choice!")

        print(filled_data)
        self.root.save_choices(filled_data)
        self.stack.set_current(self.done)

    def init(self):

        self.current_question = 0

        with flx.VBox():

            flx.Label(text="KTH Sidescan Modeling Questionnaire", style='font-size: 20px; background: #9d9; color: #FFF; font-weight: bold; text-align: center;')

            self.questions = []
            with flx.StackLayout(flex=1) as self.stack:
                self.questions.append(UserDetails())
                for key, val in choices.items():
                    self.questions.append(FolderChooser(key, val))
                self.done = DoneScreen()

            with flx.HBox():
                self.previous = flx.Button(text="Previous")
                flx.Widget(flex=1)  # Add a spacer
                self.t1 = flx.Label(text="Question 1/" + len(self.questions))
                self.submit = flx.Button(text="Submit", disabled=True)
                self.submit.apply_style("background: #D3D3D3;")
                flx.Widget(flex=1)  # Add a spacer
                self.next = flx.Button(text="Next")


class MainApp(flx.PyComponent):
#class MainApp(flx.Widget):

    def init(self):
        self.main_widget = Questionnaire()

    @flx.action
    def save_choices(self, data):
        rnd_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        filename = data["name"].replace(' ', '_') + "_" + rnd_string + ".json"
        with open(filename, 'w') as fp:
            json.dump(data, fp)


if __name__ == '__main__':
    #m = flx.launch(ThemedForm, 'app')
    #flx.run()
    #app = flx.App(Questionnaire)
    app = flx.App(MainApp)
    app.serve('')
    flx.start()
