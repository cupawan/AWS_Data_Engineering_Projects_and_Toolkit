import datetime
import pytz
import yaml
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
import os
from telegram_message import TelegramMessage


class GarminSleepData:
    def __init__(self,config_file_path):
        self.config_file_path = config_file_path
        self.config = self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file_path,'r') as file:
                config = yaml.safe_load(file)
                return config
        except Exception as e:
            d = {}
            print("Error loading configuration")
            return d
        
    def get_sleep_data(self):
        today = datetime.date.today()
        # past = today - datetime.timedelta(days=1)
        api = Garmin(self.config["MY_EMAIL_ADDRESS"], self.config["MY_GARMIN_PASSWORD"])
        try:
            api.login()
        except Exception as e:
            print("Error loggin in GarminAPI")
            return None
        sleep_data = api.get_sleep_data(today.isoformat())
        return sleep_data
    
    def seconds_to_hm(self, n_seconds):
        hours = n_seconds // 3600
        minutes = (n_seconds % 3600) // 60
        if hours != 0 and minutes != 0:
            return f"{hours} Hours {minutes} Minutes"
        elif hours == 0:
            return f"{minutes} Minutes"
        elif minutes == 0:
            return f"{hours} Hours"
        else:
            return f"{n_seconds} seconds"        

    def message_formatter(self, sleep_data):
        calendar_date = sleep_data['dailySleepDTO']['calendarDate']
        date_object = datetime.datetime.strptime(calendar_date, '%Y-%m-%d')
        formatted_date = date_object.strftime('%A, %dth %b %Y')

        sleep_score = sleep_data['dailySleepDTO']['sleepScores']['overall']['value']
        total_duration = sleep_data['dailySleepDTO']['sleepScores']['totalDuration']['qualifierKey'].title()
        total_sleep_seconds = sleep_data['dailySleepDTO']['sleepTimeSeconds']
        avg_sleep_stress = sleep_data['dailySleepDTO']['avgSleepStress']

        awake_count = sleep_data['dailySleepDTO']['sleepScores']['awakeCount']['qualifierKey'].title()
        awake_seconds = sleep_data['dailySleepDTO']['awakeSleepSeconds']
        awake_value = sleep_data['dailySleepDTO']['awakeCount']
        awake_start = int(sleep_data['dailySleepDTO']['sleepScores']['awakeCount']['optimalStart'])
        awake_end = int(sleep_data['dailySleepDTO']['sleepScores']['awakeCount']['optimalEnd'])

        rem_percentage = sleep_data['dailySleepDTO']['sleepScores']['remPercentage']['qualifierKey'].title()
        rem_value = sleep_data['dailySleepDTO']['sleepScores']['remPercentage']['value']
        rem_seconds = sleep_data['dailySleepDTO']['remSleepSeconds']
        rem_start = int(sleep_data['dailySleepDTO']['sleepScores']['remPercentage']['optimalStart'])
        rem_end = int(sleep_data['dailySleepDTO']['sleepScores']['remPercentage']['optimalEnd'])

        light_seconds = sleep_data['dailySleepDTO']['lightSleepSeconds']
        light_percentage = sleep_data['dailySleepDTO']['sleepScores']['lightPercentage']['qualifierKey'].title()
        light_value = sleep_data['dailySleepDTO']['sleepScores']['lightPercentage']['value']
        light_start = int(sleep_data['dailySleepDTO']['sleepScores']['lightPercentage']['optimalStart'])
        light_end = int(sleep_data['dailySleepDTO']['sleepScores']['lightPercentage']['optimalEnd'])

        restlessness = sleep_data['dailySleepDTO']['sleepScores']['restlessness']['qualifierKey'].title()
        restless_moments_count = sleep_data['restlessMomentsCount']

        deep_seconds = sleep_data['dailySleepDTO']['deepSleepSeconds']
        deep_percentage = sleep_data['dailySleepDTO']['sleepScores']['deepPercentage']['qualifierKey'].title()
        deep_value = sleep_data['dailySleepDTO']['sleepScores']['deepPercentage']['value']
        deep_start = int(sleep_data['dailySleepDTO']['sleepScores']['deepPercentage']['optimalStart'])
        deep_end = int(sleep_data['dailySleepDTO']['sleepScores']['deepPercentage']['optimalEnd'])

        body_battery_change  = sleep_data['bodyBatteryChange']
        resting_heartrate = sleep_data['restingHeartRate']
        
        summary_message = f"{formatted_date}\nYou slept for {self.seconds_to_hm(total_sleep_seconds)}\nScore: {sleep_score}/100 ({total_duration})\n\n" \
                        f"REM Sleep: {rem_percentage}\n\t{self.seconds_to_hm(rem_seconds)}\n\tScore: {rem_value} [Optimal: ({rem_start} - {rem_end})]\n\n" \
                        f"Light Sleep: {light_percentage}\n\t{self.seconds_to_hm(light_seconds)}\n\tScore: {light_value} [Optimal: ({light_start} - {light_end})]\n\n" \
                        f"Deep Sleep: {deep_percentage}\n\t{self.seconds_to_hm(deep_seconds)}\n\tScore: {deep_value} [Optimal: ({deep_start} - {deep_end})]\n\n" \
                        f"Awake: {awake_count}\n\t{self.seconds_to_hm(awake_seconds)}\n\tScore: {awake_value} [Optimal: ({awake_start} - {awake_end})]\n\n" \
                        f"Average Sleep Stress: {avg_sleep_stress}\n" \
                        f"Body Battery Change: {body_battery_change}\n" \
                        f"Resting Heart Rate: {resting_heartrate}\n" \
                        f"Restlessness Level: {restlessness}\nRestless moments: {restless_moments_count}"\
        
        return summary_message


def lambda_handler(event,context):
# if __name__ == "__main__":
    my_garmin = GarminSleepData(config_file_path= "config.yaml")
    tg = TelegramMessage(config_file_path= "config.yaml")
    try: 
        sleep_data = my_garmin.get_sleep_data()    
        msgbody = my_garmin.message_formatter(sleep_data=sleep_data)
        tg.send_message(message_type = "photo", caption = msgbody, chat_id= tg.config["TELEGRAM_CHAT_IDS"]["PAWAN"], data = "SleepStats.png")
        return {'statusCode':200}
    except Exception as e:
        tg.send_message(message_type = "text", caption = msgbody, chat_id= tg.config["TELEGRAM_CHAT_IDS"]["PAWAN"], data = str(e))
        return {'statusCode':400}


    

        
    
    
