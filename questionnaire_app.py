#!/usr/bin/python3

from flexx import flx, event, config
from tornado.web import StaticFileHandler
import string
import random
import json
import os
from datetime import datetime

config.hostname = "localhost"
config.port = 8097
dirname = "/home/nbore/Data/gan_generated_results"
subdir1 = "1"
subdir2 = "2"
nbr_from_1 = 20
nbr_from_2 = 10

folders_in_1 = [o for o in os.listdir(os.path.join(dirname, subdir1)) if os.path.isdir(os.path.join(dirname, subdir1, o))]
folders_in_2 = [o for o in os.listdir(os.path.join(dirname, subdir2)) if os.path.isdir(os.path.join(dirname, subdir2, o))]

class NoCacheStaticFileHandler(StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

# Make use of Tornado's static file handler
tornado_app = flx.create_server().app
tornado_app.add_handlers(r".*", [
        (r"/images/(.*)", NoCacheStaticFileHandler, {"path": dirname}),
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
                            self.ims.append(flx.ImageWidget(stretch=False, source="/images/"+self.choicedir+"/"+c, minsize=(452., 852.)))

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
                        #self.i0 = flx.ImageWidget(source="/images/"+self.choicedir+"/q.png", style="zoom: 2;")
                        self.i0 = flx.ImageWidget(source="/images/"+self.choicedir+"/q.png", minsize=(452., 702.))
                        self.i1 = flx.ImageWidget(source="/images/"+self.choicedir.split('/')[0]+"/colorbar.png")
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

        help_string1 = """At KTH, we are experimenting with different ways of generating sidescan waterfall images
                          from bathymetry. In our current research, we would like to collect input from experts on
                          sidescan sonar. If you are used to looking at sidescan sonar images, we would therefore be
                          very thankful if you could fill out the following questionnaire. The results are completely
                          anonymous, and it should take approximately 10 minutes to fill out."""


        help_string2 = """Instructions: first, fill in a few details that help us categorize the responses.
                          Then click the "Next" button in the lower right corner. You will be presented with
                          a small piece of bathymetry and two sidescan waterfall images. Please choose the one
                          that you judge to be most realistic given the presented bathymetry. Note that both or
                          none of the images might be absolutely realistic. Click the button "1" or "2" corresponding
                          to the image and then click "Next". Repeat the procedure until you you reached the end
                          and have one selection for each image pair. You then need to click the "Submit" button
                          to finish the questionnaire."""


        help_string3 = "If you have any questions, please contact: Nils Bore, nbore@kth.se"

        with flx.VBox():

            flx.Widget(minsize=20)  # Add a spacer
            flx.Label(text=help_string1, wrap=1)
            flx.Widget(minsize=20)  # Add a spacer
            flx.Label(text=help_string2, wrap=1)
            flx.Widget(minsize=20)  # Add a spacer
            flx.Label(text=help_string3, wrap=1)
            flx.Widget(flex=1)  # Add a spacer

            with flx.HFix(flex=1):
                flx.Widget(flex=1)  # Add a spacer
                with flx.FormLayout(flex=1) as self.form:
                    flx.Widget(flex=1)  # Add a spacer
                    self.name = flx.LineEdit(title='Profession:', text='', maxsize=(600, 0))
                    self.affiliation = flx.LineEdit(title='Affiliation:', text='', maxsize=(600, 0))
                    with flx.HBox():
                        flx.Label(text="Familiarity with sidescan (0-10):")
                        self.familiarity = self.tension = flx.Slider(min=0, max=10, value=5,
                                                                     text=lambda: 'Familiarity: {value}', flex=1)
                    flx.Label(text='When done, click the "Next" button')
                    flx.Widget(flex=1)  # Add a spacer
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

class SubmitScreen(flx.Widget):

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

        self.do_submit = flx.Label(text='If you made a choice for each pair of images you should now be able to click the "Submit" button below!', wrap=1)


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
        self.stack.set_current(self.do_submit)

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
                if ind == 0:
                    filled_data[q.choicedir] = (q.choices[1], q.choices[2])
                else:
                    filled_data[q.choicedir] = (q.choices[2], q.choices[1])
            except ValueError:
                filled_data[q.choicedir] = "None"
                print("Could not find choice!")

        print(filled_data)
        self.root.save_choices(filled_data)
        self.stack.set_current(self.done)

    def init(self, choices):

        self.current_question = 0

        with flx.VBox():

            flx.Label(text="KTH Sidescan Modeling Questionnaire", style='font-size: 20px; background: #9d9; color: #FFF; font-weight: bold; text-align: center;')

            self.questions = []
            with flx.StackLayout(flex=1) as self.stack:
                self.questions.append(UserDetails())
                for key, val in choices.items():
                    self.questions.append(FolderChooser(key, val))
                self.do_submit = SubmitScreen()
                self.done = DoneScreen()

            with flx.HBox():
                self.previous = flx.Button(text="Previous")
                flx.Widget(flex=1)  # Add a spacer
                self.t1 = flx.Label(text="Question 1/" + len(self.questions))
                self.submit = flx.Button(text="Submit", disabled=True)
                self.submit.apply_style("background: #D3D3D3;")
                flx.Widget(flex=1)  # Add a spacer
                self.next = flx.Button(text="Next")


#class MainApp(flx.PyComponent):
class MainApp(flx.PyComponent):
#class MainApp(flx.Widget):

    def init(self):

        self.rnd_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        choices = {}
        random.shuffle(folders_in_1)
        for i in folders_in_1[:nbr_from_1]:
            options = ["1.png", "2.png", "3.png"]
            random.shuffle(options)
            choices[subdir1+"/"+i] = ["q.png"] + options[:2]

        random.shuffle(folders_in_2)
        for i in folders_in_2[:nbr_from_2]:
            options = ["1.png", "2.png", "3.png"]
            random.shuffle(options)
            choices[subdir2+"/"+i] = ["q.png"] + options[:2]
        self.main_widget = Questionnaire(choices)

    @flx.action
    def save_choices(self, data):
        rnd_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        filename = data["name"].replace(' ', '_') + "_" + self.rnd_string + "_" + rnd_string + ".json"
        data["time"] = str(datetime.now())
        with open(filename, 'w') as fp:
            json.dump(data, fp)

if __name__ == '__main__':
    #m = flx.launch(ThemedForm, 'app')
    #flx.run()
    #app = flx.App(Questionnaire)
    app = flx.App(MainApp)
    app.serve('')
    flx.start()
