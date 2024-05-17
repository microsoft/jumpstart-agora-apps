# Autor: Armando Blanco
# Date: 2023-Nov-07
# Version: 0.9
# Description: Script to simulate data from a fryer and a production line

import json
import random
import datetime
import time
#from datetime import date, timedelta, time, datetime
import os
import paho.mqtt.client as mqtt
import random

# MQTT broker details
broker_address = "127.0.0.1"  # Replace with your MQTT broker's address
#broker_address = os.environ.get("MQTT_BROKER", "mqtt.eclipse.org")

broker_port = 1883  # MQTT broker port (default is 1883)
#broker_port = int(os.environ.get("MQTT_PORT", 1883))

# Frecuency to send data in seconds
frecuency=10

# MQTT topics to publish to
topic1 = "topic/weldingrobot"  
topic2 = "topic/assemblybatteries"
topic3 = "topic/assemblyline" 
topic4 = "topic/assemblylineInfluxDb" 

# Create MQTT clients for each topic
# UPDATE DERIVATED POF NEW PAHO LIB
client_id1 = f'python-mqtt-{random.randint(0, 1000)}'
client1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id1)

client_id2 = f'python-mqtt-{random.randint(0, 1000)}'
client2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id2)

client_id3 = f'python-mqtt-{random.randint(0, 1000)}'
client3 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id3)

client_id4 = f'python-mqtt-{random.randint(0, 1000)}'
client4 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id4)

# Connect to the MQTT broker for each client
client1.connect(broker_address, broker_port)
client2.connect(broker_address, broker_port)
client3.connect(broker_address, broker_port)
client4.connect(broker_address, broker_port)

maintenance_last_generated = datetime.datetime.now()
production_last_generated = datetime.datetime.now()

#HISTORICAL_DATA_DAYS_ARG = int(os.environ.get("HISTORICAL_DATA_DAYS", 7))
HISTORICAL_DATA_DAYS_ARG = 7
HISTORICAL_DATA_DAYS = (0-HISTORICAL_DATA_DAYS_ARG)  # This is to generate date prior to current date for dashboards.

# Define common schema templates to generate telemetry data
plant_details = [ 
    { "plant_id": "PT-01", "location": "Detroit, MI" },
    { "plant_id": "PT-02", "location": "Mexico City, MX" },
    { "plant_id": "PT-03", "location": "Shanghai, CN" },
    { "plant_id": "PT-04", "location": "Hamburg, DE" }
]

production_schedule = {"production_date": "2024-03-20", "scheduled_start": "20:00", "scheduled_end": "08:00", "planned_production_time_hours": 12, "actual_production_time_hours": 10}

employees = [
    {"employee_id": "E-001", "name": "John Doe", "role": "supervisor"},
    {"employee_id": "E-002", "name": "Jane Smith", "role": "engineer"},
    {"employee_id": "E-003", "name": "Mike Johnson", "role": "technician"}
]

cars_produced = [
    {"assembly_line": "AL-01", "car_id": "E-001", "model": "Sedan", "color": "red", "engine_type": "electric", "assembly_status": "none", "quality_check": "none" },
    {"assembly_line": "AL-02", "car_id": "H-002", "model": "SUV", "color": "blue", "engine_type": "hybrid", "assembly_status": "none", "quality_check": "none" },
    {"assembly_line": "AL-03", "car_id": "G-003", "model": "Coupe", "color": "black", "engine_type": "gasoline", "assembly_status": "none", "quality_check": "none" }
]

equipment_info = [
    {
        "equipment_id": "EQ-001",
        "type": "assembly_robot",
        "maintenance_schedule": "30d",
        "technical_specs": {}
    },
    {
        "equipment_id": "EQ-002",
        "type": "conveyor_belt",
        "maintenance_schedule": "10d",
        "technical_specs": {}
    },
    {
        "equipment_id": "EQ-003",
        "type": "paint_station",
        "maintenance_schedule": "90d",
        "technical_specs": {}
    },
    {
        "equipment_id": "EQ-004",
        "type": "welding-assembly_robot",
        "model": "RoboArm X2000",
        "maintenance_schedule": "15d",
        "arm_reach": "1.5 meters",
        "load_capacity": "10 kg",
        "precision": "0.02 mm",
        "rotation": "360 degrees"
    },
    {
        "equipment_id": "WLD-001",
        "type": "welding_robot",
        "model": "WeldMaster 3000",
        "maintenance_schedule": "5d",
        "welding_speed": "1.5 meters per minute",
        "welding_technologies": ["MIG", "TIG"],
        "maximum_thickness": "10 mm",
        "precision": "+/- 0.5 mm"
    }
]

# Equipment 
equipment_maintenance_history = [
    {
        "equipment_id": "WLD-001",
        "date": "2024-03-20",
        "start_time": "10:21",
        "end_time": "12:30",
        "type": "routine_check",
        "notes": "All systems operational, no issues found."
    },
    {
        "equipment_id": "WLD-001",
        "date": "2024-01-15",
        "start_time": "8:00",
        "end_time": "8:30",
        "type": "repair",
        "notes": "Replaced servo motor in joint 3."
    }
]

maintenance_types = [ 
    { "type": "routine_check", "message": "All systems operational, no issues found" },
    { "type": "emergency_check", "message": "Equipment is in critical condition, need immediate attention" }
]

production_shifts = [ 
    { "shift":"morning", "utc_start_hour":0, "utc_end_hour":7 },
    { "shift":"afternoon", "utc_start_hour":8, "utc_end_hour":15 },
    { "shift":"night", "utc_start_hour":16, "utc_end_hour":23 }    
]

# Function to generate simulated data
def generate_dataWelding():
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
def generate_batteriesdata():
    # Get the current time in ISO format
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    waste_reasons = ["", "Overcooked", "Undercooked", "Machine Error"]
    lost_time_reasons = ["", "Machine Breakdown", "Raw Material Shortage", "Power Outage"]
    
    # Prepare the JSON payload
    return {
        "Timestamp": current_time,
        "MakeupArea": "Plant Germany - Build",
        "Line": "Line 1 - Battery",
        "Product": "Battery",
        "Process": "Pack Production",
        "Batch": random.randint(1, 10),
        "CurrentShift": random.choice(["Shift 1", "Shift 2", "Shift 3"]),
        "CurrentCellAssemblyPerMinutes": random.randint(130, 150),
        "TargetCellAssemblyPerMinutes": 145,
        "StartTime": current_time,
        "FinishTime": (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%d-%m-%Y %H:%M:%S.%f'),
        "Waste": random.uniform(1, 2),
        "WasteReason": random.choice(waste_reasons),
        "LostTime": "SPT",
        "LostTimeReason": random.choice(lost_time_reasons),
        "LostTimeTimeCount": random.randint(90, 100),
        "ScheduledBatteries": random.randint(8, 12),
        "CompletedBatteries": random.randint(3, 7),
        "ScheduledBatteriesPerHour": random.randint(280, 320),
        "Temperature": random.uniform(230, 240),
        "ImpactTest": random.uniform(780, 790),
        "VibrationTest": random.uniform(6, 7),
        "CellTest": random.uniform(400, 410),
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
        "OEE_GoalbyPlant": random.uniform(78, 82),
        "OEE_Seattle": random.uniform(95, 96),
        "OEE_Detroit": random.uniform(95, 96),
        "OEE_Hannover": random.uniform(95, 96),
        "OEE_USA": random.uniform(95, 96),
        "OEE_Mexico": random.uniform(95, 96),
        "OEE_GoalbyProduct": random.uniform(78, 82),
        "OEE_BatteryA": random.uniform(96, 97),
        "OEE_BatteryB": random.uniform(94, 95),
        "OEE_BatteryC": random.uniform(95, 96),
        "OEE_GoalbyShift": random.uniform(78, 82),
        "OEE_MorningShift": random.uniform(92, 94),
        "OEE_DayShift": random.uniform(86, 88),
        "OEE_NightShift": random.uniform(88, 90)
    }

# Get shift information
def get_shift(current_date_time):
    for shift in production_shifts:
        if current_date_time.hour >= shift['utc_start_hour'] and current_date_time.hour <= shift['utc_end_hour']:
            return shift['shift']

# produce this randomly with random delay between  1 to 3 hours
def simulate_equipment_maintenance(current_time):
    return {
        "equipment_id": "WLD-001",              # Pick random equipment
        "maintenance_date": str(current_time.date),
        "start_time": "10:21",                  # Produce random
        "end_time": "12:30",                    # Add random duration
        "type": "routine_check",
        "notes": "All systems operational, no issues found."
    }

# Produce equipment telemetry every 30 seconds or a minute
def simulate_equipment_telemetry(current_time):
    # Convert time string
    current_time = str(current_time)

    equipment_telemetry = [
        # Assembly Robot
        {
            "date_time": current_time,
            "equipment_id": "EQ-001",
            "type": "assembly_robot",
            "status": random.choice(["operational", "maintenance_required"]),   # Instead of random, use periodic maintenance
            "operational_time_hours": random.uniform(10, 12),
            "cycles_completed": random.randint(3400, 3500),
            "efficiency": random.uniform(93, 97),
            "maintenance_alert": random.choice(["none", "scheduled_check", "urgent_maintenance_required"]), # Instead of random, use periodic maintenance alerts
            "last_maintenance": "2024-02-20",
            "next_scheduled_maintenance": "2024-04-01"
        },
        # Conveyor Belt
        {
            "date_time": current_time,
            "equipment_id": "EQ-002",
            "type": "conveyor_belt",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(10, 12),
            "distance_covered_meters": random.randint(10000, 12000),
            "efficiency": random.uniform(98, 99),
            "maintenance_alert": random.choice(["none", "scheduled_check"]),
            "last_maintenance": "2024-03-15",
            "next_scheduled_maintenance": "2024-03-30"
        },
        # Paint Station
        {
            "date_time": current_time,
            "equipment_id": "EQ-003",
            "type": "paint_station",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(7, 9),
            "units_processed": random.randint(400, 500),
            "efficiency": random.uniform(90, 93),
            "maintenance_alert": random.choice(["none", "urgent_maintenance_required"]),
            "last_maintenance": "2024-02-25",
            "next_scheduled_maintenance": "Overdue"
        },
        # Welding-Assembly Robot
        {
            "date_time": current_time,
            "equipment_id": "EQ-004",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(10, 12),
            "cycles_completed": random.randint(3400, 3500),
            "efficiency": random.uniform(94, 96),
            "maintenance_alert": random.choice(["none", "scheduled_check"]),
            "last_maintenance": "2024-03-20",
            "next_scheduled_maintenance": "2024-04-01",
            "average_cycle_time": "10 seconds",
            "failures_last_month": random.randint(1, 3),
            "success_rate": random.uniform(98.5, 99.9)
        },
        # Welding Robot
        {
            "date_time": current_time,
            "equipment_id": "WLD-001",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(9, 11),
            "welds_completed": random.randint(5100, 5300),
            "efficiency": random.uniform(97, 99),
            "maintenance_alert": random.choice(["none", "scheduled_check"]),
            "last_maintenance": "2024-03-22",
            "next_scheduled_maintenance": "2024-04-05",
            "average_weld_time": "30 seconds",
            "failures_last_month": random.randint(0, 3),
            "success_rate": random.uniform(98, 99.9)
        }
    ]

    return equipment_telemetry

# Update assembly status with progress, start with in_progress and end with completed. Update status every 1 minutes
def simulate_production_telemetry():
    # Once the status completed change production id
    for car in cars_produced:
        car['assembly_status'] = random.choice(["completed", "in_progress"])
        if car['assembly_status'] == "completed":
            car['quality_check'] = random.choice(["pass", "fail"])

    return cars_produced

# Produce this data for every 8 hours
def simulate_production_by_shift():
    return {}

# Generate performance metrics
def generate_performance_metrics():
    return {
        "availability_oee": random.uniform(0.95, 0.99),
        "reject_rate": random.uniform(0.04, 0.06),
        "comments": "Minor downtime due to equipment maintenance. Overall production efficiency remains high."
    }

# Generate actual production data
def generate_actual_production_data(date_time):
    return {
        "start_time": "20:00",
        "end_time": "07:30",
        "actual_production_time_hours": 11.5,
        "production_downtime_hours": 0.5,
        "units_manufactured": random.randint(690, 710),
        "units_rejected": random.randint(30, 40),
        "utc_hour": "20", 
        "units_produced": random.randint(55, 60), 
        "units_rejected": random.randint(2, 4)
    
    }

# Produce assembly production data every minute for realtime data and every hour for historical data
def simulate_assembly_line_data(date_time):

    # Get current shift
    current_shift = get_shift(date_time)

    # Produce cars production progress data every time this method is called
    cars_produced = simulate_production_telemetry()

    # Produce cars production stats every one hour
    global maintenance_last_generated
    if int((date_time - maintenance_last_generated).total_seconds() / 60) > 5:
        actual_production = simulate_production_by_shift()
    else:
        actual_production = {}

    # Produce equipment telemetry data every time this method is called
    equipment_telemetry = simulate_equipment_telemetry(date_time)

    # Produce equipment maintenance data every 5 minutes
    global production_last_generated
    if int((date_time - production_last_generated).total_seconds() / (5 *60)) > 5:
        equipment_maintenance = simulate_equipment_maintenance(date_time)
        maintenance_last_generated = date_time
    else:
        equipment_maintenance = {}

    # Make this by shift  production information
    actual_production = generate_actual_production_data(date_time)
    
    # Include in the hourly production performance metrics
    performance_metrics = generate_performance_metrics()

    # Split this into hourly and by shift
    current_time = date_time.isoformat() + "Z"
    simulation_data = {
        "date_time": current_time,
        "plant_details": plant_details[random.randint(0, len(plant_details)-1)],
        "shift": current_shift,
        "employees_on_shift": employees,
        "cars_produced": cars_produced,
        "equipment_maintenance": equipment_maintenance,
        "production_schedule": production_schedule,
        "actual_production": actual_production,
        "equipment_telemetry": equipment_telemetry,
        "performance_metrics": performance_metrics
    }

    return simulation_data

# Function to send data to MQTT broker
def send_to_mqtt(data1, data2, data3):

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

        # Prepare the JSON payload for the second topic
        payload3 = {
            "Content-Type": "application/json",  # Property "Content-Type"
            "data": data3  # Data in JSON format
        }
        payload_json3 = json.dumps(payload3)

        # Publish the data to the first topic
        client1.publish(topic1, payload=payload_json1.encode('utf-8'))
        print(f"Published to {topic1}: {payload_json1}")

        # Publish the data to the second topic
        client2.publish(topic2, payload=payload_json2.encode('utf-8'))
        print(f"Published to {topic2}: {payload_json2}")

        # Publish the data to the second topic
        client3.publish(topic3, payload=payload_json3.encode('utf-8'))
        print(f"Published to {topic3}: {payload_json3}")
    
    except Exception as e:
        print(f"\n Error sending data:", e)

# Main function
if __name__ == "__main__":
    
    # Connect to the MQTT broker for each client
    # client1.connect(broker_address, broker_port)
    # client2.connect(broker_address, broker_port)
    # Generate batch and continue with live data

    number_of_days = HISTORICAL_DATA_DAYS
    production_datetime = datetime.datetime.now() + datetime.timedelta(days=number_of_days)
    
    
    while True:
        try:
            # Generate simulated data
            simulated_data_welding = generate_dataWelding()
            simulated_data_batteries = generate_batteriesdata()
            #simulated_data_assembly_line = simulate_assembly_line_data()

            #assembly line
            # Generate live data
            print('Now generating live date...')
            current_time = datetime.datetime.now()
            # Produce equipment telemetry data every 30 seconds
            print('Generating for: ', production_datetime)
            simulated_data_assembly_line = simulate_assembly_line_data(current_time)
            #send_product_to_event_hub(simulated_data)

            # Send the data to the MQTT broker
            send_to_mqtt(simulated_data_welding, simulated_data_batteries, simulated_data_assembly_line)

            # Wait for the next cycle
            time.sleep(frecuency) 

            print(f"\n Sent data")

        except KeyboardInterrupt:
            print("Ctrl+C detected. Exiting...")
            client1.disconnect()
            client2.disconnect()
            break
