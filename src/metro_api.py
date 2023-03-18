import time
from config import config

class MetroApiOnFireException(Exception):
    pass

class MetroApi:
    def __init__(self):
        pass

    def fetch_train_predictions(self, wifi, station_code: str) -> [dict]:
        return self._fetch_train_predictions(wifi, station_code, retry_attempt=0)

    def _fetch_train_predictions(self, wifi, station_code: str, retry_attempt: 
                                 int) -> [dict]:
        try:
            print("Fetching...")

            # Counter potential null values in API response, as python doesn't recognize null
            null = None

            # Construct a URL that will fetch data for our desired station
            api_url = config['metro_api_url'] + station_code

            # Fetch data for our desired station from the URL
            response = wifi.get(api_url, headers={'api_key': config['metro_api_key']},
                                timeout=1).json()

            # Filter train data so only objects for our selected group are in the list.
            trains = list(filter(lambda t: t['Group'] == config['train_group'], 
                          response['Trains']))
            print("Received response from API. The filtered result:")
            print(trains)
            
            # Switch to showing result for both groups if there are no trains with assigned lines 
            # in the selected group AND the user wants result from both lines in this instance. 
            # This can be useful when single-tracking occurs and one group switches to the other.
            # 'No psngr' trains with no assigned lines are ignored in figuring the group to show.            
            trains_test = list(filter(lambda t: t['Line'] in ['BL', 'GR', 'OR', 'RD', 'SV', 'YL'], 
                                      trains))
            if not trains_test and config['show_all_groups_if_nothing_else']:
                print("No trains with an assigned line in this group.")
                trains_alt = list(response['Trains'])
                trains_alt = trains_alt[:config['num_trains']]
                print("The re-filtered result, expanded to include the other one or two groups:")
                print(trains_alt)
                trains_test = list(filter(lambda t: t['Line'] in ['BL', 'GR', 'OR', 'RD', 'SV',
                                   'YL'], trains_alt))
                if not trains_test:
                    print("No trains with an assigned line in any group, so using the initial \
                          result as the basis for display.")
                else:
                    trains = list(response['Trains'])
                    print("Using the re-filtered result as the basis for display.")
                            
            # Convert train objects list to a custom list with data needed for display
            trains = [self._normalize_train_response(t) for t in trains][:config['num_trains']]
            print("Normalized train response:")
            for train in trains:
                print(train)

            return trains

        except Exception as e:
            print(e)
            if retry_attempt < config['metro_api_retries']:
                print("Failed to connect to API. Retrying...")
                # Recursion for retry logic because I don't care about your stack
                time.sleep(config['refresh_interval'])
                return self._fetch_train_predictions(wifi, station_code, 
                                                     retry_attempt + 1)
            else:
                raise MetroApiOnFireException()

    # Take a JSON object for single train and return only the data needed for display
    def _normalize_train_response(self, train: dict) -> dict:
        line = train['Line']
        line = self._get_line_color(line)

        car = train['Car']
        car = self._get_corrected_car_value(car)

        destination = train['Destination']
        destination = self._get_corrected_dest_case(destination)
        destination = self._get_corrected_dest_value(destination)

        min = train['Min']
        min = self._get_corrected_min_value(min)

        return {
            'line': line,
            'car': car,
            'destination': destination,
            'min': min
        }

    # Convert two-letter 'line" value into equivalent integer
    def _get_line_color(self, line: str) -> int:
        if line == 'BL':
            return 0x0000FF
        elif line == 'GR':
            return 0x00FF00
        elif line == 'OR':
            return 0xFF5500
        elif line == 'RD':
            return 0xFF0000
        elif line == 'SV':
            return 0xAAAAAA
        elif line == 'YL':
            return 0xFFFF00
        else:
            return 0x000000

    # Respond to empty 'car' value
    def _get_corrected_car_value(self, car: str) -> str:
        if car is None:
            car = '-'
        return car
    
    # Convert 'Destination' WMATA API result from all caps to title case
    def _get_corrected_dest_case(self, destination: str) -> str:
        # The WMATA API sometimes reports 'Destination' in all caps. Changing from all caps to 
        # titlecase takes extra work because .title() does not work in CircuitPython. 
        all_caps = 0
        dest_replace = ""
        if len(destination) > 0 and destination.isupper():
            destination = destination.lower()
            for word in destination.split():
                dest_replace += word[0].upper() + word[1:] + " "    
            dest_replace = dest_replace.rstrip()
            destination = dest_replace
        return destination
    
    # Correct for problems in 'Destination' WMATA API result
    def _get_corrected_dest_value(self, destination: str) -> str:
        # The 'Destination' reported by the WMATA API sometimes needs correcting. For instance, 
        # instead of 'NewCrltn', the API may use 'N Carrollton', which is too long to display 
        # properly. To address this, a dictionary is used to correct for known and potential 
        # problems in API-reported data. Also included in the dictionary any extra-long 
        # destinations that we don't want cropped, such as the 9-char 'Gallry Pl' (which displays
        # OK despite its length when using a variable-width font).
        # If the 1st string appears in any part of Destination, replace Destination with 2nd string
        dest_corrections = {
            'No Passenger': 'No Psngr',
            'NoPssenger': 'No Psngr',
            'ssenger': 'No Psngr',
            'Branch': 'Brnch Av',
            'Brnch Ave': 'Brnch Av',
            'Carroll': 'NewCrltn',
            'Chinatown': 'Gallry Pl',
            'Downtown': 'Largo',
            'DT Largo': 'Largo',
            'Dulles': 'Dulles',
            'Fairfax': 'Fairfax',
            'Farragut N': 'Frgut N.',
            'Fran/': 'Frnconia',
            'Franconia': 'Frnconia',
            'Ft. Tottn': 'Ft.Tottn',
            'Gallery': 'Gallry Pl',
            'Gallry Pl': 'Gallry Pl',
            'GallryPl': 'Gallry Pl',
            'Greenbelt': 'Grnbelt',
            'Grosvnor': 'Grsvnor',
            'Huntington': 'Hntingtn',
            'NoMa': 'NoMa',
            'Noma': 'NoMa',
            'R.i.': 'R.I.',
            'Rhode': 'R.I.',
            'Shady': 'Shady Gr',
            'Silver': 'SilvrSpr',
            'Silvrspr': 'SilvrSpr',
            'Totten': 'Ft.Tottn',
            'U St': 'U St',
            'Vernon': 'Mt. Vern',
            'W Falls': 'W Fls Ch',
            'West Falls': 'W Fls Ch'
        }
        dest_replace = ""
        for key in dest_corrections.keys():
            if key in destination:
                dest_replace = dest_corrections[key]
        if dest_replace:
            destination = dest_replace
        else:
            destination = destination[:config['dest_max_characters']]
        return destination
    
    # Reduce three-character 'min' values to two characters, to save space on the train board
    def _get_corrected_min_value(self, min: str) -> str:
        if min == 'ARR':
            min = 'AR'
        if min == 'BRD':
            min = 'BD'
        if min == '---' or min == '':
            min = 'DL'
        return min
