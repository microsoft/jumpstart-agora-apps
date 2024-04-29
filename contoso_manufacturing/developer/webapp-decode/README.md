# Agora Manufacturing UI

## Quickstart

1. Clone the repository
1. Download all the requirements
    ```bash
    pip install -r requirements.txt
    ```
1. Run Grafana container to use `IFrame` for rendering the Dashboards
    ```bash
    docker run -d -p 3000:3000 --name=grafana -v ./grafana:/var/lib/grafana -v ./grafana/custom.ini:/etc/grafana/grafana.ini grafana/grafana
    ```
1. Login to Grafana, and create a Dashbaord
1. Get the **Embedded** link of the Grafana Dashboard Frame (Dashboard -> MyDashboard -> Frame -> Share -> Embedded)
1. Run the Flask python app
    ```bash
    python .\main.py
    ```
1. Navigate to the browser and click around for the different videos and dashboards