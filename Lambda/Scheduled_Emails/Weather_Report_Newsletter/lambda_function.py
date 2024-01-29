from OpenWeatherMap import OpenWeatherMap
from SendEmail import EmailWithPython


def lambda_handler(event,context):
    contacts = {'username@gmail.com' :[('latitude_value', 'longitude_value'),'location/address','name']}
    owm = OpenWeatherMap(config_path='config.yaml')
    gc = EmailWithPython(config_path = "config.yaml", is_html = True)
    for key,value in contacts.items():
        rec_mail = key
        name = value[-1]
        location,latitude,longitude  = value[1],value[0][0],value[0][1]
        body = owm.request_weather_data(lat = latitude, lon=longitude, name = name, location=location)
        if body:
            gc.send_email(rec_email=rec_mail,subject="Today's Weather Report",body = body)
            print("Email Sent to {}".format(name))
            