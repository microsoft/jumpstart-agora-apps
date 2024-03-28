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
topic3 = "topic/assemblyline"  

# Create MQTT clients for each topic
# UPDATE DERIVATED POF NEW PAHO LIB
client_id1 = f'python-mqtt-{random.randint(0, 1000)}'
#client1 = mqtt.Client(client_id1)  PAHO LIB - UPDATE FEB 2024
client1 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id1)

client_id2 = f'python-mqtt-{random.randint(0, 1000)}'
#client2 = mqtt.Client(client_id2) PAHO LIB - UPDATE FEB 2024
client2 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id2)

client_id3 = f'python-mqtt-{random.randint(0, 1000)}'
#client2 = mqtt.Client(client_id2) PAHO LIB - UPDATE FEB 2024
client3 = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id3)

# Connect to the MQTT broker for each client
client1.connect(broker_address, broker_port)
client2.connect(broker_address, broker_port)
client3.connect(broker_address, broker_port)

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

def simulate_assembly_line_data():
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    employees = [
        {"employee_id": "E-001", "name": "John Doe", "role": "supervisor"},
        {"employee_id": "E-002", "name": "Jane Smith", "role": "engineer"},
        {"employee_id": "E-003", "name": "Mike Johnson", "role": "technician"}
    ]

    cars_produced = [
        {"car_id": "C-001", "model": "Sedan", "color": "red", "engine_type": "electric", "assembly_status": "completed"},
        {"car_id": "C-002", "model": "SUV", "color": "blue", "engine_type": "hybrid", "assembly_status": "completed"},
        {"car_id": "C-003", "model": "Coupe", "color": "black", "engine_type": "gasoline", "assembly_status": "in_progress"}
    ]

    # Randomly update the assembly status for the cars
    for car in cars_produced:
        car['assembly_status'] = random.choice(["completed", "in_progress"])


    equipment_telemetry = [
        # Assembly Robot
        {
            "equipment_id": "EQ-001",
            "type": "assembly_robot",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(10, 12),
            "cycles_completed": random.randint(3400, 3500),
            "efficiency": random.uniform(93, 97),
            "maintenance_alert": random.choice(["none", "scheduled_check", "urgent_maintenance_required"]),
            "last_maintenance": "2024-02-20",
            "next_scheduled_maintenance": "2024-04-01"
        },
        # Conveyor Belt
        {
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
            "equipment_id": "EQ-004",
            "type": "welding-assembly_robot",
            "model": "RoboArm X2000",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(10, 12),
            "cycles_completed": random.randint(3400, 3500),
            "efficiency": random.uniform(94, 96),
            "maintenance_alert": random.choice(["none", "scheduled_check"]),
            "last_maintenance": "2024-03-20",
            "next_scheduled_maintenance": "2024-04-01",
            "technical_specs": {
                "arm_reach": "1.5 meters",
                "load_capacity": "10 kg",
                "precision": "0.02 mm",
                "rotation": "360 degrees"
            },
            "operation_stats": {
                "average_cycle_time": "10 seconds",
                "failures_last_month": random.randint(1, 3),
                "success_rate": random.uniform(98.5, 99.9)
            },
            "maintenance_history": [
                {
                    "date": "2024-03-20",
                    "type": "routine_check",
                    "notes": "All systems operational, no issues found."
                },
                {
                    "date": "2024-01-15",
                    "type": "repair",
                    "notes": "Replaced servo motor in joint 3."
                }
            ]
        },
        # Welding Robot
        {
            "equipment_id": "WLD-001",
            "type": "welding_robot",
            "model": "WeldMaster 3000",
            "status": random.choice(["operational", "maintenance_required"]),
            "operational_time_hours": random.uniform(9, 11),
            "welds_completed": random.randint(5100, 5300),
            "efficiency": random.uniform(97, 99),
            "maintenance_alert": random.choice(["none", "scheduled_check"]),
            "last_maintenance": "2024-03-22",
            "next_scheduled_maintenance": "2024-04-05",
            "technical_specs": {
                "welding_speed": "1.5 meters per minute",
                "welding_technologies": ["MIG", "TIG"],
                "maximum_thickness": "10 mm",
                "precision": "+/- 0.5 mm"
        },
            "operation_stats": {
            "average_weld_time": "30 seconds",
            "failures_last_month": random.randint(0, 3),
            "success_rate": random.uniform(98, 99.9)
        },
        "maintenance_history": [
                {
                    "date": "2024-03-22",
                    "type": "routine_check",
                    "notes": "Checked welding nozzles and gas supply. All systems go."
                },
                {
                    "date": "2024-02-28",
                    "type": "repair",
                    "notes": "Repaired gas flow regulator."
                }
            ]
        }
    ]

    production_schedule = {"scheduled_start": "20:00", "scheduled_end": "08:00", "total_production_time_hours": 12}

    actual_production = {
        "start_time": "20:00",
        "end_time": "07:30",
        "actual_production_time_hours": 11.5,
        "production_downtime_hours": 0.5,
        "units_manufactured": random.randint(690, 710),
        "units_rejected": random.randint(30, 40),
        "details": [
            {"hour": "20-21", "units_produced": random.randint(55, 60), "units_rejected": random.randint(2, 4)},
            # Additional hourly details can be added here
        ]
    }

    performance_metrics = {
        "availability_oee": random.uniform(0.95, 0.99),
        "reject_rate": random.uniform(0.04, 0.06),
        "comments": "Minor downtime due to equipment maintenance. Overall production efficiency remains high."
    }

    simulation_data = {
        "date": current_time,
        "assembly_line_info": {
            "line_id": "AL-789",
            "location": "Detroit, MI",
            "shift": "night",
            "employees_on_shift": employees,
            "cars_produced": cars_produced
        },
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

    while True:
        try:
            # Generate simulated data
            simulated_data = generate_dataFryer()
            simulated_dataPL = generate_productionlinedata()
            simulated_data_assembly_line = simulate_assembly_line_data()

            # Send the data to the MQTT broker
            send_to_mqtt(simulated_data, simulated_dataPL, simulated_data_assembly_line)

            # Wait for the next cycle
            time.sleep(frecuency) 

            print(f"\n Sent data")

        except KeyboardInterrupt:
            print("Ctrl+C detected. Exiting...")
            client1.disconnect()
            client2.disconnect()
            break
