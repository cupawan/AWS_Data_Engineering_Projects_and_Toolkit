import os
import yaml
import json
import requests
import csv
from datetime import datetime
import pytz
from SendEmail import EmailWithPython
import pandas as pd

class OpenWeatherMap:
    def __init__(self, config_path):
        self.config_path = config_path
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.config = self.load_config()

    def load_config(self):
        config_path = os.path.join(self.current_dir, self.config_path)
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            print("Error loading API_KEY")
            return {"API_KEY":"NO_KEY"}

    def save_csv(self, data):
        filepath = os.path.join(self.current_dir, 'Geocoding.csv')
        if not os.path.exists(filepath):
            with open(filepath, 'a+') as data_file:
                csvwriter = csv.writer(data_file)
                csvwriter.writerows([["Address", "Latitude", "Longitude"], data])
        else:
            with open(filepath, 'a+') as data_file:
                csvwriter = csv.writer(data_file)
                csvwriter.writerow(data)
   
    def epcoch_to_dtobj(self,ep):
        datetime_object_utc = datetime.utcfromtimestamp(ep)
        target_timezone = pytz.timezone('Asia/Kolkata')
        datetime_object_target_timezone = datetime_object_utc.replace(tzinfo=pytz.utc).astimezone(target_timezone)
        formatted_datetime = datetime_object_target_timezone.strftime("%d %b %I:%M %p")
        return formatted_datetime

    def geocode(self, address, limit=1):
        params = {'q': address, 'limit' : limit, 'appid' : self.config['API_KEY']}
        response = requests.get(url=self.config["GEOCODE"],params = params).json()[0]
        data = [address, response['lat'], response['lon']]
        self.save_csv(data=data)
        return response['lat'], response['lon']
    
    def request_weather_data(self,lat,lon, name, location):
        params = {'lat': lat, 'lon' : lon, 'appid' : self.config['API_KEY'],'units' : 'metric'}
        response = requests.get(url = self.config["CURRENT_WEATHER"],params=params)
        if response.status_code == 200:
            data = response.json()['current']
            cols = ["Data & Time", "Sunrise", "Sunset", "Tempreture", "Feels Like", "Pressure", "Humidity", "Dew Point", "UV Index", "Clouds", "Visibility", "Wind Speed", "Wind Degree"]
            vals = [str(self.epcoch_to_dtobj(data['dt'])),str(self.epcoch_to_dtobj(data['sunrise'])),str(self.epcoch_to_dtobj(data['sunset'])),f"{data['temp']}°C",f"{data['feels_like']}°C",f"{data['pressure']}mb",f"{data['humidity']}%",f"{data['dew_point']}°C",str(data["uvi"]),f"{data['clouds']}%",f"{data['visibility']} Metres",f"{data['wind_speed']}m/s",str(data['wind_deg'])]
            email_body = f"""
                        <html>
                        <head>
                            <style>
                                body {{
                                    font-family: 'Arial', sans-serif;
                                    background-color: #f4f4f4;
                                    color: #333;
                                }}
                                table {{
                                    width: 80%;
                                    margin: 20px auto;
                                    border-collapse: collapse;
                                    border: 1px solid #ddd;
                                }}
                                th, td {{
                                    padding: 12px;
                                    text-align: left;
                                    border-bottom: 1px solid #ddd;
                                }}
                                th {{
                                    background-color: #f2f2f2;
                                }}
                            </style>
                        </head>
                        <body>

                        <h2>Weather Information</h2>

                        <table>
                            <tr>
                                <th>Data & Time</th>
                                <td>{vals[0]}</td>
                            </tr>
                            <tr>
                                <th>Sunrise</th>
                                <td>{vals[1]}</td>
                            </tr>
                            <tr>
                                <th>Sunset</th>
                                <td>{vals[2]}</td>
                            </tr>
                            <tr>
                                <th>Temperature</th>
                                <td>{vals[3]}</td>
                            </tr>
                            <tr>
                                <th>Feels Like</th>
                                <td>{vals[4]}</td>
                            </tr>
                            <tr>
                                <th>Pressure</th>
                                <td>{vals[5]}</td>
                            </tr>
                            <tr>
                                <th>Humidity</th>
                                <td>{vals[6]}</td>
                            </tr>
                            <tr>
                                <th>Dew Point</th>
                                <td>{vals[7]}</td>
                            </tr>
                            <tr>
                                <th>UV Index</th>
                                <td>{vals[8]}</td>
                            </tr>
                            <tr>
                                <th>Clouds</th>
                                <td>{vals[9]}</td>
                            </tr>
                            <tr>
                                <th>Visibility</th>
                                <td>{vals[10]}</td>
                            </tr>
                            <tr>
                                <th>Wind Speed</th>
                                <td>{vals[11]}</td>
                            </tr>
                            <tr>
                                <th>Wind Degree</th>
                                <td>{vals[12]}</td>
                            </tr>
                        </table>

                        </body>
                        </html>
                        """
            weather_report = f"""
                                <html>
                                <head>
                                    <style>
                                        body {{
                                            font-family: 'Arial', sans-serif;
                                            background-color: #eff8ff;
                                            color: #333;
                                            margin: 20px;
                                        }}
                                        .report-container {{
                                            max-width: 600px;
                                            margin: 0 auto;
                                            padding: 20px;
                                            border: 2px solid #3498db;
                                            border-radius: 10px;
                                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                                            background-color: #fff;
                                        }}
                                        .highlight {{
                                            color: #e74c3c;
                                            font-weight: bold;
                                        }}
                                        .important {{
                                            background-color: #f8d7da;
                                            padding: 2px;
                                            color: #721c24;
                                            border-radius: 3px;
                                        }}
                                    </style>
                                </head>
                                <body>

                                <div class="report-container">
                                    <h2>Weather Report</h2>
                                    <h3>Good Morning, {name}</h3>

                                    <p>
                                        The current weather report for <span class="highlight">{vals[0]}</span> at  <span class="highlight">{location}</span> is as follows:
                                    </p>

                                    <p>
                                        <strong>Sunrise:</strong> {vals[1]} | <strong>Sunset:</strong> {vals[2]}
                                    </p>

                                    <p>
                                        The temperature is <span class="highlight">{vals[3]}</span>, and it feels like <span class="highlight">{vals[4]}</span>. The atmospheric pressure is <span class="highlight">{vals[5]}</span>,
                                        humidity is <span class="highlight">{vals[6]}</span>, and the dew point is <span class="highlight">{vals[7]}</span>.
                                    </p>

                                    <p>
                                        The UV Index is <span class="highlight">{vals[8]}</span>, clouds cover <span class="highlight">{vals[9]}</span> of the sky, and visibility is <span class="highlight">{vals[10]}</span>.
                                    </p>

                                    <p>
                                        Wind speed is <span class="highlight">{vals[11]}</span>, coming from <span class="highlight">{vals[12]}</span> degrees.
                                    </p>
                                    <p> Have a nice day! </p>
                                </div>

                                </body>
                                </html>
                                """
    
            return weather_report
        else:
            print("RESPONSE CODE: ",response.status_code)
            return None
