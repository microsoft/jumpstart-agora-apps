# Autor: Armando Blanco
# Date: 2023-Nov-07
# Version: 0.9
# Description: Script to simulate data from a fryer and a production line

import json
import random
import datetime
import time
import os
import paho.mqtt.client as mqtt

# MQTT broker details
broker_address = os.environ.get("MQTT_BROKER", "mqtt.eclipse.org")

#broker_port = 1883  # MQTT broker port (default is 1883)
broker_port = int(os.environ.get("MQTT_PORT", 1883))

# Frecuency to send data in seconds
frecuency = int(os.environ.get("FRECUENCY", 20))  # Frecuency to send data in seconds

# MQTT topics to publish to
topic1 = "topic/fryer"  
topic2 = "topic/productionline"  

# Create MQTT clients for each topic
client1 = mqtt.Client()
client2 = mqtt.Client()

# Connect to the MQTT broker for each client
client1.connect(broker_address, broker_port)
client2.connect(broker_address, broker_port)

# Function to generate simulated data
def generate_dataFryer():
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    return {
        "Timestamp": current_time,
        "Heater_Outlet_Temp": random.uniform(70, 80),
        "Pump1_Flow_Totalizer": random.uniform(85000, 86000),
        "Pump2_Flow_Totalizer": random.uniform(75000, 77000),
        "Pump3_Flow_Totalizer": random.uniform(129000, 130000),
        "Pump1_Temperature_Flow": random.uniform(20, 30),
        "Pump2_Temperature_Flow": random.uniform(20, 30),
        "Pump3_Temperature_Flow": random.uniform(20, 30),
        "Pumps_Total_Flow": random.uniform(30, 35),
        "Pressure_Filter_Inlet": random.uniform(1, 2),
        "Pressure_Filter_Outlet": random.uniform(0.5, 1.5),
        "RobotPosition_J0": random.uniform(0, 5),
        "RobotPosition_J1": random.uniform(0, 5),
        "RobotPosition_J2": random.uniform(0, 5),
        "RobotPosition_J3": random.uniform(0, 5),
        "RobotPosition_J4": random.uniform(0, 5),
        "RobotPosition_J5": random.uniform(0, 5),
        "Tank_Level": random.uniform(60, 70),
        "Drive1_Current": random.uniform(0.4, 0.6),
        "Drive1_Frequency": 30,
        "Drive1_Speed": 30,
        "Drive1_Voltage": random.uniform(190, 200),
        "Drive2_Current": random.uniform(0.4, 0.6),
        "Drive2_Frequency": 30,
        "Drive2_Speed": 30,
        "Drive2_Voltage": random.uniform(190, 200),
        "Drive3_Current": random.uniform(0.4, 0.6),
        "Drive3_Frequency": 30,
        "Drive3_Speed": 30,
        "Drive3_Voltage": random.uniform(190, 200),
        "Cooler_Inlet_Temp": random.uniform(70, 80),
        "Cooler_Outlet_Temp": random.uniform(70, 80),
        "Dynamix_Ch1_Acceleration": random.uniform(0.02, 0.03),
        "Flow001": random.uniform(3, 4),
        "Pressure001": random.uniform(1, 2),
        "Pressure002": random.uniform(0.4, 0.6),
        "Heater_Inlet_Temp": random.uniform(70, 80),
        "Pump1_Conductivity": random.uniform(55, 65),
        "Valve_000_Pump1": random.choice([True, False]),
        "Cooler_ON": random.choice([True, False]),
        "Fan001_On": random.choice([True, False]),
        "Heater_ON": random.choice([True, False]),
        "Filter_Chg_Required": random.choice([True, False]),
        "Filter_Reset": random.choice([True, False]),
        "Filter_Override": random.choice([True, False]),
        "UTC_Time": current_time,
        "Current": random.uniform(0, 0.01),
        "Voltage": random.uniform(100, 110),
        "Temperature": random.uniform(70, 80),
        "Humidity": random.uniform(40, 50),
        "VacuumAlert": random.choice([True, False]),
        "VacuumPressure": random.uniform(10, 20),
        "Oiltemperature": random.uniform(350, 390),
        "OiltemperatureTarget": 375
    }

#Function to generate simulated data for production line
def generate_productionlinedata():
    # Get the current time in ISO format
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    waste_reasons = ["", "Overcooked", "Undercooked", "Machine Error"]
    lost_time_reasons = ["", "Machine Breakdown", "Raw Material Shortage", "Power Outage"]
    
    # Prepare the JSON payload
    return {
        "Timestamp": current_time,
        "MakeupArea": "Plant Seattle - Ignite",
        "Line": "Line 1 - Donuts",
        "Product": "Strawnberry Donuts ",
        "Process": "Mixer",
        "Batch": random.randint(1, 10),
        "CurrentShift": random.choice(["Shift 1", "Shift 2", "Shift 3"]),
        "CurrentCutPerMinutes": random.randint(130, 150),
        "TargetCutPerMinutes": 145,
        "StartTime": current_time,
        "FinishTime": (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%d-%m-%Y %H:%M:%S.%f'),
        "Waste": random.uniform(1, 2),
        "WasteReason": random.choice(waste_reasons),
        "LostTime": "SPT",
        "LostTimeReason": random.choice(lost_time_reasons),
        "LostTimeTimeCount": random.randint(90, 100),
        "ScheduledDoughs": random.randint(8, 12),
        "CompletedDoughs": random.randint(3, 7),
        "ScheduledDoughsPerHour": random.randint(280, 320),
        "DoughTemperature": random.uniform(230, 240),
        "Weight": random.uniform(780, 790),
        "Height": random.uniform(6, 7),
        "OvenTemp": random.uniform(400, 410),
        "DownTime": random.randint(2, 6),
        "Thruput": random.randint(28, 32),
        "OverallEfficiency": random.randint(88, 92),
        "Availability": random.randint(93, 97),
        "Performance": random.randint(93, 97),
        "Quality": random.randint(93, 97),
        "PlannedProductionTime": random.randint(58, 62),
        "ActualRuntime": random.randint(960, 965),
        "UnplannedDowntime": random.randint(295, 300),
        "PlannedDowntime": 0,
        "PlannedQuantity": random.randint(290, 310),
        "ActualQuantity": random.randint(280, 290),
        "RejectedQuantity": random.randint(10, 20),
        "OEEGoalbyPlant": random.uniform(78, 82),
        "OEESeattle": random.uniform(95, 96),
        "OEEMiami": random.uniform(94, 95),
        "OEEBoston": random.uniform(95, 96),
        "OEEMexicoCity": random.uniform(95, 96),
        "OEEGoalbyCountry": random.uniform(78, 82),
        "OEEUSA": random.uniform(95, 96),
        "OEEMexico": random.uniform(95, 96),
        "OEEGoalbyProduct": random.uniform(78, 82),
        "OEEDonuts": random.uniform(96, 97),
        "OEECakes": random.uniform(94, 95),
        "OEEBreads": random.uniform(95, 96),
        "OEEGoalbyShift": random.uniform(78, 82),
        "OEEMorningShift": random.uniform(92, 94),
        "OEEDayShift": random.uniform(86, 88),
        "OEENightShift": random.uniform(88, 90)
    }

# Function to send data to MQTT broker
def send_to_mqtt(data1, data2):

    try:
        # Prepare the JSON payload for the first topic
        payload1 = {
            "Content-Type": "application/json",  # Property "Content-Type"
            "data": data1  # Data in JSON format 
        }
        payload_json1 = json.dumps(payload1)

        # Prepare the JSON payload for the second topic
        payload2 = {
            "Content-Type": "application/json",  # Property "Content-Type"
            "data": data2  # Data in JSON format
        }
        payload_json2 = json.dumps(payload2)

        # Publish the data to the first topic
        client1.publish(topic1, payload=payload_json1.encode('utf-8'))
        print(f"Published to {topic1}: {payload_json1}")

        # Publish the data to the second topic
        client2.publish(topic2, payload=payload_json2.encode('utf-8'))
        print(f"Published to {topic2}: {payload_json2}")
    
    except Exception as e:
        print(f"\n Error sending data:", e)

# Main function
if __name__ == "__main__":
    
    # Connect to the MQTT broker for each client
    # client1.connect(broker_address, broker_port)
    # client2.connect(broker_address, broker_port)

    while True:
        try:
            # Generate simulated data
            simulated_data = generate_dataFryer()
            simulated_dataPL = generate_productionlinedata()

            # Send the data to the MQTT broker
            send_to_mqtt(simulated_data, simulated_dataPL)

            # Wait for the next cycle
            time.sleep(frecuency) 

            print(f"\n Sent data")

        except KeyboardInterrupt:
            print("Ctrl+C detected. Exiting...")
            client1.disconnect()
            client2.disconnect()
            break
