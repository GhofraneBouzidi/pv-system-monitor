# PV System Monitor

A real-time monitoring dashboard for a photovoltaic installation. Voltage, current, power,
module temperature and efficiency stream in from an Arduino over USB and are plotted live
in a six-page Streamlit interface, with an alert panel that reacts to abnormal readings.

The dashboard runs in two modes: connected to an Arduino, or on simulated data, so it can
be demonstrated without any hardware present.

| Part | File | Runs on |
|------|------|---------|
| Dashboard (IHM) | `app.py` | PC, Python 3.9+ |
| Sensor node | `arduino/pv_sensor_node/pv_sensor_node.ino` | Arduino Uno/Nano |

The interface language is French.

## Features

- **Six pages** reachable from both a sidebar and a top navigation bar: overview,
  electrical analysis, power and energy, thermal management, performance, history
- **Live metrics** for voltage, current, power, temperature and efficiency, each with a
  delta against its nominal value
- **Floating alert panel** covering abnormal voltage, low current (possible shading),
  overcurrent, module overheating, low efficiency and low power output
- **Temperature-corrected efficiency** using a real module coefficient of −0.45 %/°C
  around a 25 °C reference
- **System health gauge** scoring voltage, current, temperature and efficiency
- **Statistics** per quantity: mean, standard deviation, min, max, median, distributions
- **Cumulative energy** tracking in Wh, plus peak power and uptime
- **Simulation mode** so the dashboard runs with no Arduino attached

## Hardware

| Component | Qty | Connects to |
|-----------|-----|-------------|
| Arduino Uno (or Nano) | 1 | USB to PC |
| Analog input — voltage | 1 | A3 |
| Analog input — current | 1 | A1 |
| Analog input — temperature | 1 | A2 |

The sketch as published reads three potentiometers on A1, A2 and A3 and maps them onto
realistic PV ranges (30–45 V, 0–10 A, 15–70 °C). This makes the full signal chain testable
on a breadboard. To drive it from a real array, replace the potentiometers with a voltage
divider, a current sensor such as an ACS712, and an LM35 or DS18B20 for module temperature,
then adjust the mapping constants at the top of the sketch.

> Never wire a PV array directly to an Arduino analog pin. Panel voltages well exceed the
> 5 V the ADC tolerates, and a divider sized for the array's open-circuit voltage is required.

## Installation

### 1. Flash the Arduino

1. Open `arduino/pv_sensor_node/pv_sensor_node.ino` in the Arduino IDE.
2. Select your board and port, then upload.
3. The Serial Monitor at 9600 baud should show a JSON line ten times a second:
   `{"voltage":36.42,"current":4.81,"temperature":38.5}`
4. **Close the Serial Monitor** before starting the dashboard; only one program can hold
   the port.

### 2. Set up Python

```bash
git clone https://github.com/<your-username>/pv-system-monitor.git
cd pv-system-monitor
pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app.py
```

The dashboard opens at http://localhost:8501. In the sidebar, pick **Mode Arduino**, choose
your COM port from the dropdown, and click **Connecter**. Leave it on **Mode Simulation**
to explore the interface without hardware.

## Serial protocol

The Arduino sends one JSON object per line at 9600 baud, ten times a second:

```json
{"voltage":36.42,"current":4.81,"temperature":38.5}
```

Power, efficiency and energy are computed on the Python side, so the sketch stays small.
Each reading is smoothed over a rolling window of ten samples before being sent.

## Alert thresholds

| Condition | Threshold | Level |
|-----------|-----------|-------|
| Abnormal voltage | < 32 V or > 45 V | warning |
| Low current, possible shading | < 1.0 A | info |
| Overcurrent | > 9.5 A | warning |
| High module temperature | > 50 °C | warning |
| Module overheating | > 65 °C | error |
| Low efficiency | < 12 % | warning |
| Very low power | < 50 W | info |

## Project structure

```
pv-system-monitor/
├── app.py                        # Streamlit dashboard: pages, charts, alerts, serial client
├── arduino/
│   └── pv_sensor_node/
│       └── pv_sensor_node.ino    # analog acquisition, smoothing, JSON output
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `Aucun port COM trouvé` | Arduino not plugged in, or its driver is missing |
| `Échec de connexion` | The Serial Monitor or another program is holding the port |
| Connected but `Aucune donnée` | Sketch not uploaded, or a baud rate other than 9600 |
| Values look random in Arduino mode | No data arrived, so the dashboard fell back to simulated values. See the note below. |
| Dashboard feels slow | Raise the refresh interval in the sidebar; each step redraws every chart |

## Known limitations

- When Arduino mode is selected but no valid frame arrives, the dashboard silently falls back
  to simulated data rather than holding the last real reading. The connection badge in the
  sidebar is the reliable indicator of what you are looking at.
- History is kept in memory only, capped at the last 200 points, and is lost when the app
  restarts. There is no export to CSV yet.
- The sketch sends ten frames a second while the dashboard refreshes at most once a second,
  so most frames are discarded and the serial buffer does the queuing.
- Efficiency is derived from temperature alone. Without an irradiance sensor it is a model,
  not a measurement.

## Roadmap

- [ ] CSV and database logging so history survives a restart
- [ ] Irradiance sensor for a true efficiency figure
- [ ] Hold the last valid reading instead of falling back to simulation
- [ ] Configurable alert thresholds from the interface
- [ ] Daily and monthly production reports

## Authors

Built as a team project by:

- **Ghofrane Bouzidi**
- **Donia El Manaa**

Supervised by **Prof. Mouez Bousaada**.

## License

MIT — see [LICENSE](LICENSE).
