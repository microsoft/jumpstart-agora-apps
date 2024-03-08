import json
import random
import datetime
import time
import os
from azure.eventhub import EventHubProducerClient, EventData
from dotenv import load_dotenv

load_dotenv()

# EventHub connection string
CONNECTION_STR=os.getenv('CONNECTION_STR')
EVENTHUB_NAME=os.getenv('EVENTHUB_NAME')
EVENTHUB_NAME_PL=os.getenv('EVENTHUB_NAME_PL')

# Generate data
def generate_data():
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

        # ... (otros campos de Drive),
        "Cooler_Inlet_Temp": random.uniform(70, 80),
        "Cooler_Outlet_Temp": random.uniform(70, 80),
        "Dynamix_Ch1_Acceleration": random.uniform(0.02, 0.03),
        # ... (otros campos de Dynamix),
        "Flow001": random.uniform(3, 4),
        # ... (otros campos de Flow),
        "Pressure001": random.uniform(1, 2),
        "Pressure002": random.uniform(0.4, 0.6),
        "Heater_Inlet_Temp": random.uniform(70, 80),
        "Pump1_Conductivity": random.uniform(55, 65),
        # ... (otros campos de Conductivity),
        "Valve_000_Pump1": random.choice([True, False]),
        # ... (otros campos de Valve),
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
        "VacuumPressure": random.uniform(10, 20)
    }
# Production line Generate data
def generate_productionlinedata():
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    waste_reasons = ["", "Overcooked", "Undercooked", "Machine Error"]
    lost_time_reasons = ["", "Machine Breakdown", "Raw Material Shortage", "Power Outage"]
    
    return {
        "Timestamp": current_time,
        "MakeupArea": "Plant Seattle - Ignite",
        "Line": "Line 1 - Donuts",
        "Product": "Min Donuts Cinnamon Sugar",
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
# Send data to EventHub
def send_to_eventhub(data1, data2):
    producer1 = EventHubProducerClient.from_connection_string(CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
    producer2 = EventHubProducerClient.from_connection_string(CONNECTION_STR, eventhub_name=EVENTHUB_NAME_PL)


    print(data2)

    try:
        # Sent to EH 1
        event_data1 = EventData(json.dumps(data1))
        producer1.send_batch([event_data1])

        event_data2 = EventData(json.dumps(data2))
        producer2.send_batch([event_data2])

    finally:
        producer1.close()
        producer2.close()
    
if __name__ == "__main__":
    while True:
        simulated_data = generate_data()
        simulated_dataPL = generate_productionlinedata()

        send_to_eventhub(simulated_data, simulated_dataPL)

        time.sleep(30)  # send data every 30 seconds
        print(f"\n Sent data: {simulated_data}")
        print(f"\n Sent data (2): {simulated_dataPL}")
