import allure
from helper.JMS.send_msg import Producer
from helper.paths import ProjectPaths


class Baplie:
    """JMS messaging pages for vessel operations"""
    
    def __init__(self):
        self.producer = None
    
    def send_bay_plan_message(self, provider_url: str = "t3://172.18.51.25:20212", 
                             queue: str = "jms/sp/InboundBayplanQueue",
                             data_path: str = ProjectPaths.DATA / "vessel_discharge_data.csv"):
        """Send bay plan message to JMS queue"""
        try:
            self.producer = Producer(provider_url, queue)
            success = self.producer.send_bay_plan_message(data_path)
            
            if success:
                print("Bay plan message sent successfully")
            else:
                raise Exception("Failed to send bay plan message")
                
        except Exception as e:
            print(f"JMS messaging error: {e}")
            raise
        
    def send_custom_message(self, message: str, provider_url: str = "t3://172.18.51.25:20212", 
                           queue: str = "jms/sp/InboundBayplanQueue"):
        """Send custom message to JMS queue"""
        try:
            self.producer = Producer(provider_url, queue)
            self.producer.send_message(message)
            print("Custom message sent successfully")
            
        except Exception as e:
            print(f"JMS messaging error: {e}")
            raise 