import zipfile
import json
import requests
import xml.etree.ElementTree as ET

import pandas as pd

from tuftsseds.siteapps.database.models import SolidMotor

THRUSTCURVE_API_SEARCH = "https://www.thrustcurve.org/api/v1/search.json"
THRUSTCURVE_API_DOWNLOAD = "https://www.thrustcurve.org/api/v1/download.json"
THRUSTCURVE_API_HEADERS = {"accept": "application/json", "Content-Type": "application/json"}

def extract_simulation_event_data(root, simulation_name, field):
    """
    Fetches event data stored in "header" of a ORK file's simulation.
    
    Args:
        root (ElementTree object): the root of the data tree to start traversing from
        simulation_name (str): The name of the simulation to parse through.
        field (str): the name of the event whose time you are interested in
            i.e. if I want the time at which the rocket left the launch pod, I 
            would pass "launchrod"
        
    Returns:
        Float: The specific time an event occured
    """
    
    for simulation in root.findall(".//simulation"):
        # Handling for case insensative
        name = simulation.find("name").text
        lower_name = name.lower()  # Convert extracted name to lowercase for comparison
        if lower_name == simulation_name:
            for simulation in root.findall(".//simulation[name='" + name + "']"):
                for event in simulation.findall('.//event'):
                    event_type = event.get('type')
                    if event_type == field:
                        event_time = event.get('time')
                        return float(event_time)


def extract_simulation_data(root, simulation_name, fields):
    """
    Fetches data stored in different indicies of a ORK file's simulation.
    
    Args:
        root (ElementTree object): the root of the data tree to start traversing from
        simulation_name (str): The name of the simulation to parse through.
        fields (int list): the indexes of the data you would like to retrieve i.e.
            ORK files store time, altitude, and vertical velocity in index 0, 1, and 2 respectively.
        
    Returns:
        List of lists: An NxN array of data based on the number of fields to grab and the time length of the launch
    """
    data_points = []
    for simulation in root.findall(".//simulation"):
        # Handling for case insensative
        name = simulation.find("name").text
        lower_name = name.lower()  # Convert extracted name to lowercase for comparison
        if lower_name == simulation_name:
            for simulation in root.findall(".//simulation[name='" + name + "']"):
                for databranch in simulation.findall('.//databranch'):
                    for datapoint in databranch.findall('.//datapoint'):
                        data = datapoint.text.strip().split(',')
                        selected_data = [data[i] for i in fields]
                        data_points.append(selected_data)
    return data_points

def dragco_vs_machnum(xml_root):
    """
    Fetches the drag coefficient as a function of mach number from an ORK file's simulation.
    
    Args:
        root (ElementTree object): the root of the data tree to start traversing from
        
    Returns:
        Two list of lists: One with drag coefficient vs mach number before the motor burnout
                            and one after motor burnout
                            
    Note:
        Expects all simulations that are to be parsed to be named "final simulation" (case insensative)
    """
    # OpenRocket stores the mach number and drag coefficient in index 26 and 30, repectively 
    selected_fields = [0, 26, 30] 
    raw_data = extract_simulation_data(xml_root, "final simulation", selected_fields)
    cleaned_data = [row for row in raw_data if all(item is not None for item in row)]
    
    burnout = extract_simulation_event_data(xml_root, "final simulation", "burnout")
    raw_motor_on = [sublist for sublist in cleaned_data if sublist[0] > burnout]
    raw_motor_off = [sublist for sublist in cleaned_data if sublist[0] <= burnout]
    
    # getting rid of the time field since it's unecessary data to store in the database
    motor_on = [sublist[1:] for sublist in raw_motor_on]
    motor_off = [sublist[1:] for sublist in raw_motor_off]
    return motor_on, motor_off
                
    
def extract_motor_data(xml_root):
    """
    Fetches the motor data stored in an ORK file to search a database for more info on the motor.
    
    Args:
        root (ElementTree object): the root of the data tree to start traversing from
        
    Returns:
        
    """
    # we use a list in case there are multiple motors in the ORK file
    motors = []
    for motor in xml_root.findall("./motor"):
        manufacturer = motor.find("manufacturer").text
        designation = motor.find("designation").text
        complete_motor = download_motor_info(manufacturer, designation)
        motors.append(complete_motor)
    return motors

def download_motor_info(manufacturer, designation):
    """
    Searches the Thrustcurve motor database via its API to download detailed motor info using
        the motor's manufacturer name and designation
    
    Args:
        manufacturer (str): the name of the motor manufacturer
        designation (str): the name of the motor
        
    Returns:
        List of lists: An NxN array of data based on the number of fields to grab and the time length of the launch
    """
    # Using the Thrustcurve API to search for a motor given that we have the manufacturer and 
    # designation from the ORK file
    search_data = {"manufacturer": manufacturer, "designation": designation, "maxResults": 5}
    search_response = requests.post(THRUSTCURVE_API_SEARCH, headers=THRUSTCURVE_API_HEADERS, json=search_data)
    search_results = search_response.json()
    motorid = search_results["results"][0]["motorId"]
    
    # motorid is then used to query Thrustcurve for specific data about the motor
    download_data = {"motorIds": [motorid], "data": "file", "maxResults": 5}
    download_response = requests.post(THRUSTCURVE_API_DOWNLOAD, headers=THRUSTCURVE_API_HEADERS, json=download_data)
    download_results = download_response.json()
    
    # thrust source data is usually provided in the API. If not, then download the datafile itself and
    # parse through it to get thrustsource
    if "samples" in download_results:
        samples = download_results["samples"]
        thrust_source = [[sample["time"], sample["thrust"]] for sample in samples]
    else:   
        data_url = "https://www.thrustcurve.org" + download_results["results"][0]["dataUrl"]
        thrust_source = download_motor_thrustsource(data_url)
    
    motor_data = ["results"][0]
    # taking certain data from the original search to add to the final dict
    motor_data["thrust_source"] = thrust_source
    motor_data["manufacturer"] = manufacturer
    motor_data["designation"] = designation
    motor_data["impulse_class"] = search_results["results"][0]["impulseClass"]
    motor_data["burnout"] = search_results["results"][0]["burnTimeS"]
    motor_data["propellent_mass"] = search_results["results"][0]["propWeightG"] / 1000 # g -> kg
    return motor_data

def download_motor_thrustsource(data_url):
    # the thrust curve data is output in a manner similar to how Thrustcurve displays the 
    # data on their site, therefore, we can access and store data similar to an xml file
    raw_thrust_curve = requests.get(data_url).text
    root = ET.fromstring(raw_thrust_curve)
    clean_thrust_source = []
    for eng_data in root.findall(".//eng-data"):
        # t = time (s) and f = force (Newtons)
        t = float(eng_data.get("t"))
        f = float(eng_data.get("f"))
        clean_thrust_source.append([t, f])
        
    return clean_thrust_source

def build_motor(xml_root):
    new_motor = extract_motor_data(xml_root)
    
    motor, _ = SolidMotor.objects.update_or_create(
        name = new_motor["designation"],
        manufacturer = new_motor["manufacturer"],
        impulse_class = new_motor["impulse_class"],
        defaults = {
            'thrust_source' : new_motor["thrust_source"],
            'burnout' : new_motor["burnout"],
            'grain_num' : new_motor["burnout"],
            
        }
    )