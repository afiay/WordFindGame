import random
import string
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

therapy_questions = [
    {"question": "What makes you feel happy?",
        "answers": ["FAMILY", "FRIENDS", "NATURE"]},
    {"question": "What do you value the most in friendships?",
        "answers": ["TRUST", "LOYALTY", "COMPANIONSHIP"]},
    {"question": "What's a place that calms you?",
        "answers": ["BEACH", "FOREST", "MOUNTAINS"]},
    {"question": "What activity makes you lose track of time?",
        "answers": ["READING", "PAINTING", "WRITING"]},
    {"question": "What emotion have you felt most this week?",
        "answers": ["JOY", "GRATITUDE", "CONTENTMENT"]}
]

scores = {1: 0, 2: 0}


class LetterButton(Button):
    def __init__(self, letter, grid, **kwargs):  # Add grid parameter here
        super().__init__(**kwargs)
        self.text = letter
        self.selected = False
        self.grid = grid  # Set the grid attribute here
        self.bind(on_press=self.mark_letter)

    def mark_letter(self, instance):
        app = App.get_running_app()
        self.selected = not self.selected
        if self.selected:
            self.background_color = [0.7, 0.7, 0.7, 1]
            app.selected_letters[self] = self.text
            self.grid.selected_word.append(self.text)  # Add this line
        else:
            self.background_color = [1, 1, 1, 1]
            del app.selected_letters[self]
            self.grid.selected_word.remove(self.text)  # And this line
        app.update_hint()


class WordGrid(GridLayout):
    def __init__(self, grid_size, answers, **kwargs):
        super().__init__(**kwargs)
        self.cols = grid_size
        self.selected_word = []
        self.answers = answers
        self.create_grid()

    def create_grid(self):
        answer_letters = [
            letter for answer in self.answers for letter in answer]
        unique_answer_letters = list(set(answer_letters))
        grid_letters = answer_letters[:]
        total_cells = self.cols * self.cols
        remaining_cells = total_cells - len(grid_letters)
        available_letters = list(
            set(string.ascii_uppercase) - set(unique_answer_letters))
        random_letters = ''.join(random.choices(
            available_letters, k=remaining_cells))
        grid_letters += list(random_letters)
        random.shuffle(grid_letters)
        for letter in grid_letters:
            # Pass self as the grid parameter here
            self.add_widget(LetterButton(letter, self))

    def generate_hint(self, word):
        if len(word) > 2:
            return word[0] + '_' * (len(word) - 2) + word[-1]
        return word


class WordFindGame(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_questions = therapy_questions[:]
        self.current_questions = self.original_questions[:]
        self.scores = {1: 0, 2: 0}
        self.main_layout = BoxLayout(orientation='vertical')
        self.turn_duration = 60
        self.correct_answer = ""
        self.selected_letters = ""  # Keep track of selected letters
        self.question_label = None  # Initialize question_label
        self.hint_label = None  # Initialize hint_label
        self.grid = None  # Initialize grid
        self.submit_button = None  # Initialize submit_button
        self.selected_letters = {}  # This will now be a dictionary

    def build(self):
        self.feedback_label = Label(size_hint_y=None, height=50, text='')
        self.main_layout.add_widget(self.feedback_label)
        self.timer_label = Label(
            size_hint_y=None, height=50, text=f"Time left: {self.turn_duration}")
        self.main_layout.add_widget(self.timer_label)
        self.display_next_question()
        return self.main_layout

    def generate_hint(self):
        # This method will generate a hint based on the correct answer and the selected letters
        hint = ['_'] * len(self.correct_answer)
        for i, letter in enumerate(self.grid.selected_word):  # Change this line
            if i < len(self.correct_answer) and self.correct_answer[i] == letter:
                hint[i] = letter
        return ''.join(hint)

    def update_hint(self):
        if self.hint_label:  # Make sure hint_label exists
            new_hint = self.generate_hint()
            self.hint_label.text = "Hint: " + new_hint

    def submit_word(self, instance):
        # Consolidate logic for word submission here, including hint updates
        selected_word = ''.join(self.grid.selected_word).upper()
        if selected_word in (answer.upper() for answer in self.current_question['answers']):
            self.scores[1] += 1
            self.feedback_label.text = "Correct answer!"
            Clock.schedule_once(lambda dt: self.display_next_question(), 1)
        else:
            self.feedback_label.text = "Incorrect answer, try again!"
            self.update_hint()  # Update hint here to reflect partially correct selections

    def display_next_question(self):
        # Set up for displaying the next question. Ensure this runs before update_hint
        if not self.current_questions:
            self.end_game()
            return

        self.clear_previous_question()
        self.current_question = random.choice(self.current_questions)
        self.current_questions.remove(self.current_question)

        # Additional setup including correct_answer and hint_label
        self.correct_answer = random.choice(
            self.current_question["answers"]).upper()

        # Initialize the grid
        self.grid = WordGrid(5, self.current_question["answers"])
        self.main_layout.add_widget(self.grid)

        # Initialize or update hint_label with the initial hint
        answer_hint = self.generate_hint()
        self.hint_label = Label(
            size_hint_y=None, height=60, text="Hint: " + answer_hint)
        # Display the question
        self.main_layout.add_widget(self.hint_label)
        self.question_label = Label(
            size_hint_y=None, height=60, text=self.current_question["question"])
        self.main_layout.add_widget(self.question_label)

        # Create and add the submit button
        self.submit_button = Button(
            text='Submit Answer', size_hint_y=None, height=50)
        self.submit_button.bind(on_press=self.submit_word)
        self.main_layout.add_widget(self.submit_button)

        # Start the timer
        self.restart_timer()

    def restart_timer(self):
        self.time_left = self.turn_duration
        if hasattr(self, 'timer_event'):
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"Time left: {self.time_left}"
        if self.time_left <= 0:
            self.end_turn()

    def submit_word(self, instance):
        selected_word = ''.join(self.grid.selected_word).upper()
        if selected_word in (answer.upper() for answer in self.current_question['answers']):
            self.scores[1] += 1
            self.feedback_label.text = "Correct answer!"
            Clock.schedule_once(lambda dt: self.display_next_question(), 1)
        else:
            self.feedback_label.text = "Incorrect answer, try again!"

    def clear_previous_question(self):
        if self.question_label:
            self.main_layout.remove_widget(self.question_label)
            self.question_label = None
        if self.hint_label:
            self.main_layout.remove_widget(self.hint_label)
            self.hint_label = None
        if self.grid:
            self.main_layout.remove_widget(self.grid)
            self.grid.selected_word.clear()
            self.grid = None
        if self.submit_button:
            self.main_layout.remove_widget(self.submit_button)
            self.submit_button = None

    def end_turn(self):
        self.timer_event.cancel()
        self.display_next_question()

    def end_game(self):
        self.timer_event.cancel()
        final_score = f"Final Score: {self.scores[1]} - {self.scores[2]}"
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=final_score))

        # Create a play again button
        play_again_button = Button(text='Play Again')
        play_again_button.bind(on_press=self.play_again)
        content.add_widget(play_again_button)

        # Create a quit button
        quit_button = Button(text='Quit')
        quit_button.bind(on_press=self.quit_game)
        content.add_widget(quit_button)

        self.popup = Popup(title='Game Over', content=content,
                           size_hint=(None, None), size=(400, 400))
        self.popup.open()

    def play_again(self, instance):
        # Close the popup
        self.popup.dismiss()
        # Reset the game
        self.reset_game()

    def quit_game(self, instance):
        # Close the popup
        self.popup.dismiss()
        # Stop the app
        App.get_running_app().stop()

    def reinitialize_game(self):
        self.feedback_label = Label(size_hint_y=None, height=50, text='')
        self.main_layout.add_widget(self.feedback_label)
        self.timer_label = Label(
            size_hint_y=None, height=50, text=f"Time left: {self.turn_duration}")
        self.main_layout.add_widget(self.timer_label)
        self.display_next_question()

    def reset_game(self):
        self.scores = {1: 0, 2: 0}
        self.current_questions = self.original_questions[:]
        self.main_layout.clear_widgets()
        self.reinitialize_game()


if __name__ == '__main__':
    WordFindGame().run()
