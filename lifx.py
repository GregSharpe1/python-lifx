#!/usr/bin/env python2
"""Interactions with Lifx"""
import sys
import getopt
import json
import requests


def pull_api_key(config_file):
    """A function to export an api key to ENV"""
    with open(config_file) as json_data_file:
        data = json.load(json_data_file)
        attribute_val = data.get("api_key")

    # Error checking
    if attribute_val is None:
        raise AttributeError('Invalid attribute supplied.')
    else:
        return attribute_val


class Lifx:
    """Handle all of the lifx interactions"""
    base_url = "https://api.lifx.com/v1/"
    api_key = pull_api_key("config.json")

    def get_lifx_state(self):
        """Return the current state of the lifx bulb"""

        endpoint = self.base_url + "lights/all"
        headers = {
            'Authorization': self.api_key
        }
        response = requests.get(endpoint, headers=headers)
        response = response.json()
        return response

    def preprocess_arguments(self, input):
        """This function is used to normal any anormalies"""
        return input.lower()

    def set_lifx_state(self, state):
        """Set the state of the lifx bulb ON/OFF"""

        endpoint = self.base_url + "lights/all/state"
        headers = {
            'Authorization': self.api_key
        }
        payload = {
            'power': self.preprocess_arguments(state)
        }
        response = requests.put(endpoint, headers=headers, data=payload)
        response = response.json()
        return response

        # TODO: FIX THIS BAD BOY
    def validate_attempted_colour(self, colour):
        """Used when attempting to set the colour of the bulb"""

        endpoint = self.base_url + "color"
        headers = {
            'Authorization': self.api_key,
        }
        response = requests.request("GET", endpoint, headers=headers,
                                    data={'string': colour})
        return response

    def set_lifx_colour(self, colour):
        """Set the colour of the lifx bulb"""

        # Use the above function to make sure the bulb is on!
        self.set_lifx_state('on')

        colour = colour.lower()

        endpoint = self.base_url + "lights/all/state"
        headers = {
            'Authorization': self.api_key
        }
        payload = {
            'color': colour
        }
        response = requests.put(endpoint, headers=headers, data=payload)
        response = response.json()
        return response

    def set_lifx_brightness(self, brightness_level):
        """Set the brightness of the lifx bulb"""

        # Value's are only allowed between 0.0 and 1.0.
        brightness_level = float(brightness_level) / 100

        # Use the above function to make sure the bulb is on!
        self.set_lifx_state('on')

        endpoint = self.base_url + "lights/all/state"
        headers = {
            'Authorization': self.api_key
        }
        payload = {
            'brightness': brightness_level
        }
        response = requests.put(endpoint, headers=headers, data=payload)
        response = response.json()
        return response

    def toggle_lifx_state(self):
        """Used to toggle the state of the lifx bulb"""

        endpoint = self.base_url + "lights/all/toggle"
        headers = {
            'Authorization': self.api_key
        }
        response = requests.post(endpoint, headers=headers)
        return response

    def get_lifx_scenes(self):
        """Return a list of created scenes"""

        endpoint = self.base_url + "scenes"
        headers = {
            'Authorization': self.api_key
        }
        response = requests.get(endpoint, headers=headers)
        response = response.json()
        return response

    def get_scene_id(self, scene_name):
        """Return the scene unique id"""

        # Let's filter through the scenes with the user provided scene_name
        # to locate the uuid
        for scenes in self.get_lifx_scenes():
            if scenes['name'] == scene_name:
                return scenes['uuid']
            else:
                raise ValueError("Cannot find {} within your lifx account! Please refer to your mobile application".format(scene_name))

    def set_lifx_scene(self, scene_name):
        """Set a lifx specific scene"""

        scene_uuid = self.get_scene_id(scene_name)

        endpoint = self.base_url + "scenes/scene_id:" + scene_uuid + '/activate'
        headers = {
            'Authorization': self.api_key
        }
        response = requests.put(endpoint, headers=headers)
        response = response.json()
        return response


def usage():
    """Print out the usage of this script"""
    print "Interaction with LIFX"
    print
    print "Usage: ./lifx.py"
    print "-h       | --help        "
    print "-c       | --colour      "
    print "-s       | --state       "
    print "-t       | --toggle      "
    print "-b       | --brightness  "
    print
    print
    print "Examples:                "
    print "./lifx.py --colour OR -c blue        - This will set the colour of the bulb"
    print "./lifx.py --state OR -s ON/OFF       - This will set the state of the bulb on or off"
    print "./lifx.py --toggle OR -t             - This will toggle the state of the bulb"
    print "./lifx.py --brightness OR -b         - This will set the brightness level of the bulb (0-100)"

    sys.exit(1)


# Main part of the script
def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:tb:",
                                   [ "help",
                                     "colour=",
                                     "state=",
                                     "toggle",
                                     "bright=" ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--colour"):
            lifx = Lifx()
            lifx.set_lifx_colour(arg)
        elif opt in ("-s", "--state"):
            lifx = Lifx()
            lifx.set_lifx_state(arg)
        elif opt in ("-t", "--toggle"):
            lifx = Lifx()
            lifx.toggle_lifx_state()
        elif opt in ("-b", "--bright"):
            lifx = Lifx()
            lifx.set_lifx_brightness(arg)
        else:
            assert False, "ERROR: Unhandled option"


if __name__ == "__main__":
    main(sys.argv[1:])
