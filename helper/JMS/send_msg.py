import os
import time
from pathlib import Path

import jpype.imports

from helper.JMS.generate_msg import generate_message

# Set up JVM and classpath
cur_dir = os.path.dirname(__file__)
weblogic_jar = os.path.join(cur_dir, "weblogic-wlthint3client-12.2.1.4.jar")
# jms_api_jar = os.path.join(cur_dir, "javax.jms-api-2.0.1.jar")  # Optional, add if needed

classpath = [weblogic_jar]
# if os.path.exists(jms_api_jar):
#     classpath.append(jms_api_jar)

# Verify JARs exist
# for jar in classpath:
#     if not os.path.exists(jar):
#         raise FileNotFoundError(f"JAR file not found: {jar}")

# Set JAVA_HOME
if not os.environ.get("JAVA_HOME", ""):
    for java_home in [
        "C:\\Program Files\\Java\\jre-1.8",
        "C:\\Program Files\\Java\\jdk-1.8",
        "C:\\Program Files\\Java\\latest\\jre-1.8\\bin",
    ]:
        if os.path.exists(java_home):
            os.environ["JAVA_HOME"] = java_home
            break
    else:
        raise EnvironmentError("JAVA_HOME not set and no valid Java installation found")

# Start JVM
if not jpype.isJVMStarted():
    try:
        jpype.startJVM(classpath=classpath)
    except Exception as e:
        raise RuntimeError(f"Failed to start JVM: {e}")

# Import Java classes
try:
    Context = jpype.JClass("javax.naming.Context")
    InitialContext = jpype.JClass("javax.naming.InitialContext")
    ConnectionFactory = jpype.JClass("javax.jms.ConnectionFactory")
    QueueConnection = jpype.JClass("javax.jms.QueueConnection")
    QueueConnectionFactory = jpype.JClass("javax.jms.QueueConnectionFactory")
    QueueRequestor = jpype.JClass("javax.jms.QueueRequestor")
    Queue = jpype.JClass("javax.jms.Queue")
    Hashtable = jpype.JClass("java.util.Hashtable")
    StringClass = jpype.JClass("java.lang.String")
except Exception as e:
    raise RuntimeError(f"Failed to load Java classes: {e}")

class Producer:
    def __init__(self, provider_url, queue) -> None:
        """Initialize JMS Producer.

        Args:
            provider_url (str): e.g., 't3://172.18.51.21:25910'
            queue (str): JMS queue name
        """
        hash_table = Hashtable()
        hash_table.put(Context.INITIAL_CONTEXT_FACTORY, "weblogic.jndi.WLInitialContextFactory")
        hash_table.put(Context.PROVIDER_URL, provider_url)
        self.queue = queue
        self.context = InitialContext(hash_table)
        self.connection_factory = self.context.lookup("weblogic/jms/ConnectionFactory")

    def send_message(self, str_message):
        connection = self.connection_factory.createQueueConnection()
        session = connection.createQueueSession(False, 1)
        queue = self.context.lookup(self.queue)
        queue_requestor = QueueRequestor(session, queue)
        connection.start()

        message = session.createTextMessage()
        message.setStringProperty("handler", "messaging.handler.SimpleHandler")
        message.setText(str_message)

        simple_reply = queue_requestor.request(message)

        reply_id = simple_reply.getJMSCorrelationID()
        body = str(simple_reply.getBody(StringClass))
        print(reply_id)
        print(body)

        # Save reply to file
        temp_dir = os.getenv("LOCALAPPDATA", "") + "\\Temp"
        print(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        with open(os.path.join(temp_dir, "reply.xml"), "w") as f:
            f.write(body)

        session.close()
        connection.close()

    def send_jms_msg(self, file_path) -> bool:
        with open(file_path, "r", encoding="UTF-8") as file:
            msg = file.read()
        self.send_message(msg)
        print(f"jms queue: {self.queue}")
        print(f"message: {msg}")
        time.sleep(5)
        print(f"Done {file_path}")
        return True

    def send_bay_plan_message(self, data_path: str = "data/vessel_discharge_data.csv") -> bool:
        """Send bay plan message using vessel discharge data"""
        try:
            # Handle both absolute and relative paths
            data_file_path = Path(data_path)
            if not data_file_path.is_absolute():
                # Try to find the file relative to project root
                project_root = Path(__file__).parent.parent.parent
                data_file_path = project_root / data_path
            
            if not data_file_path.exists():
                raise FileNotFoundError(f"Data file not found: {data_file_path}")
                
            msg = generate_message(data_file_path)
            self.send_message(msg)
            print(f"Bay plan message sent to queue: {self.queue}")
            return True
        except Exception as e:
            print(f"Failed to send bay plan message: {e}")
            return False

if __name__ == "__main__":
    try:
        producer = Producer(
            "t3://172.18.51.25:20212",
            "jms/sp/InboundBayplanQueue",  # Bayplan
        )
        cur_path = os.path.dirname(os.path.abspath(__file__))
        cur_dir = os.path.dirname(cur_path)
        data_path = Path("data/vessel_discharge_data.csv")
        msg = generate_message(data_path)
        # print(msg)
        producer.send_message(msg)
        print(f"{producer.queue} sent")
        # print(f"{msg}")
        print("Done")
    finally:
        if jpype.isJVMStarted():

            jpype.shutdownJVM()