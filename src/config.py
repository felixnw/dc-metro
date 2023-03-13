from adafruit_bitmap_font import bitmap_font

config = {

    #########################
    # Network Configuration #
    #########################

    # WIFI Network SSID
    'wifi_ssid': '<Your 2.4ghz WiFi SSID>',
    
    # WIFI Password
    'wifi_password': '<Your wifi password>',

    #########################
    # Metro Configuration   #
    #########################

    # Metro Station Code
    # See https://github.com/GJT-34/dc-metro/blob/main/README.md for a list of stations. 
    # Arrival information for up to two stations can be displayed.
    'metro_station_code': 'A01', 

    # Metro Train Group
    # 'Group' is loosely a synonym for track.
    # See https://github.com/GJT-34/dc-metro/blob/main/README.md for a list of which groups 
    # correspond to which destinations on each line.
    'train_group': '1',

    # Show All Groups If Nothing Else to Show
    # If there are no trains with assigned lines in the selected group, we can show results for
    # all groups instead. This can help when there is single-tracking, during which time trains
    # in one group are switched to another group. 
    'show_all_groups_if_nothing_else': True,

    # API Key for WMATA
    'metro_api_key': 'd3adb33fd3adb33fd3adb33f',

    #########################
    # Other Values You      #
    # Probably Shouldn't    #
    # Touch                 #
    #########################

    'metro_api_url': 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/',
    'metro_api_retries': 2,
    'refresh_interval': 5,

    # Display Settings
    'matrix_width': 64,
    'num_trains': 3,
    'font': bitmap_font.load_font('lib/Metroesque.bdf'),
    # Metroesque font characters are GENERALLY 5px wide (including 1px for left padding) but are 
    # always 7px tall
    #   M, m, T, V, v, W, w, & Y are 6px wide
    #   I, i, & l are 4px wide
    #   Space is 2px wide
    'character_width': 5,
    'character_height': 7,
    'bottom_text_padding': 1,

    'text_color': 0xFF5500,  # ORANGE 
    'text_color_8-car': 0x00FF00,  # GREEN
    'heading_color': 0xFF0000,  # RED
    'header': (("LN", 0, 0), ("CAR", 0, 12), ("DST", 0, 29), ("MIN", 1, 65),),

    # Size of color-coded line indicator rectangle
    'train_line_width': 3,
    'train_line_height': 7,

    # Default text loaded for each of the up-to-three "train" info lines
    'line_pos': 0,
    'loading_car_text': '-',
    'car_pos': 6,
    'loading_dest_text': 'Loading',
    'dest_pos': 13,
    'loading_min_text': '--',
    'min_pos': 65,
    'loading_line_color': 0xFF00FF,  # MAGENTA
    'dest_max_characters': 8,
}
