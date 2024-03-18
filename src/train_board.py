import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix
from config import config

# Main display board that holds and updates all the pixels and data based on api data
class TrainBoard:
    """
    get_new_data is a function designed to return an array of dictionaries:
    [
        {
            'line': 0xFFFFFF,
            'car': '6',
            'destination': 'Dest Str',
            'min': '5'
        }
    ]
    """
    def __init__(self, get_new_data):
        # Function callback for API
        self.get_new_data = get_new_data

        # Object that will display our groups
        self.display = Matrix().display

        # Group that holds our objects (e.g., Rect()s and Label()s)
        self.parent_group = displayio.Group()

        # Build the heading labels
        for head in config['header']:
            self.heading = Label(
                config['font'],
                color=config['heading_color'],
                text=head[0],
                anchor_point=(head[1], 0),  # Top left (0, 0) or top right (1, 0) of label box
                anchored_position=(head[2], 0),  # x & y board location of the anchor point
                )
            self.parent_group.append(self.heading)

        # Create the main list that holds the references to our three sub-groups of train data
        # (this is not an actual displayio.Group(), just a class with data)
        self.trains = []
        for i in range(config['num_trains']):
            self.trains.append(Train(self.parent_group, i))

        # Show the board (will default to loading screen on startup)
        self.display.show(self.parent_group)

    def refresh(self) -> bool:
        train_data = self.get_new_data()

        # If we have successfully received our data from API, then update train info based on 
        # what we received
        if train_data:
            # Turn on screen and set brightness to full
            self.display.brightness = 1
            print("Reply received.")
            for i in range(config['num_trains']):
                if i < len(train_data):
                    train = train_data[i]
                    self._update_train(
                        i,
                        train['line'],
                        train['car'],
                        train['destination'],
                        train['min'],
                    )
                else:
                    self._hide_train(i)

            print("Successfully updated.")
        else:
            # Turn off screen and set brightness to zero
            self.display.brightness = 0
            print("No data received. Clearing display.")

            for i in range(config['num_trains']):
                self._hide_train(i)

    def _hide_train(self, index: int):
        self.trains[index].hide()

    def _update_train(self, index: int, line:
                      int, car: str, destination: str, minutes: str):
        self.trains[index].update(line, car, destination, minutes)

# Class for holding data that defines a row of train info
class Train:
    def __init__(self, parent_group, index):
        # Get the y value of the current train section
        y = (int)(config['character_height'] + config['bottom_text_padding']) * (index + 1)

        # Build the rect that shows the line (color) of the incoming train
        self.line_rect = Rect(
            config['line_pos'], 
            y,
            config['train_line_width'],
            config['train_line_height'],
            fill=config['loading_line_color'],
        )

        self.car_label = Label(
            config['font'],
            color=config['text_color'],
            text=config['loading_car_text'],
            anchor_point=(0, 0),
            anchored_position=(config['car_pos'], y),
        )

        self.destination_label = Label(
            config['font'],
            color=config['text_color'],
            text=config['loading_dest_text'],
            anchor_point=(0, 0),
            anchored_position=(config['dest_pos'], y),
        )

        self.min_label = Label(
            config['font'],
            color=config['text_color'],
            text=config['loading_min_text'],
            anchor_point=(1, 0),
            anchored_position=(config['min_pos'], y),
        )

        self.group = displayio.Group()
        self.group.append(self.line_rect)
        self.group.append(self.car_label)
        self.group.append(self.destination_label)
        self.group.append(self.min_label)

        parent_group.append(self.group)

    def show(self):
        self.group.hidden = False

    def hide(self):
        self.group.hidden = True

    def set_line(self, line: int):
        self.line_rect.fill = line

    def set_car(self, car: str):
        car = str(car)
        self.car_label.text = car
        if car == "8":
            self.car_label.color = config['text_color_8-car']
        else:
            self.car_label.color = config['text_color']

    def set_destination(self, destination: str):
        self.destination_label.text = destination

    def set_min(self, min: str):
        minutes = str(min)
        self.min_label.text = minutes

    def update(self, line: int, car: str, destination: str, min: str):
        self.show()
        self.set_line(line)
        self.set_car(car)
        self.set_destination(destination)
        self.set_min(min)
