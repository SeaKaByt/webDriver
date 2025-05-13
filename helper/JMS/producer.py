import os
import time

cur_dir = os.path.dirname(__file__)
os.environ["CLASSPATH"] = os.path.join(cur_dir, "weblogic-wlthint3client-12.2.1.4.jar")

if not os.environ.get("JAVA_HOME", ""):
    for java_home in [
        "C:\\Program Files\\Java\\jre-1.8",
        "C:\\Program Files\\Java\\jdk-1.8",
        "C:\\Program Files\\Java\\latest\\jre-1.8\\bin",
    ]:
        if os.path.exists(java_home):
            os.environ["JAVA_HOME"] = java_home

# from bs4 import BeautifulSoup
import jpype.imports


class Producer:
    # Load necessary Java classes
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

    def __init__(self, provider_url, queue) -> None:
        """_summary_

        Args:
            provider_url (str): 't3://172.18.51.21:25910'
            # hpukiut1-mvp-l01.hphit.hutchisonports.com:30152
            queue (str): _description_
        """
        hash_table = self.Hashtable()
        hash_table.put(
            self.Context.INITIAL_CONTEXT_FACTORY,
            "weblogic.jndi.WLInitialContextFactory",
        )
        hash_table.put(self.Context.PROVIDER_URL, provider_url)
        self.queue = queue
        self.context = self.InitialContext(hash_table)  # properties
        self.connection_factory = self.context.lookup("weblogic/jms/ConnectionFactory")

    def send_message(self, str_message):
        connection = self.connection_factory.createQueueConnection()
        session = connection.createQueueSession(False, 1)
        queue = self.context.lookup(self.queue)
        queue_requestor = self.QueueRequestor(session, queue)
        connection.start()

        message = session.createTextMessage()
        message.setStringProperty("handler", "messaging.handler.SimpleHandler")
        message.setText(str_message)

        simple_reply = queue_requestor.request(message)

        reply_id = simple_reply.getJMSCorrelationID()
        body = simple_reply.getBody(self.StringClass)
        print(reply_id)
        print(body)

        # save reply to file
        temp_dir = os.getenv("LOCALAPPDATA", "") + "\\Temp"
        with open(temp_dir + "\\reply.xml", "w") as f:
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

    @property
    def sample_message(self) -> str:
        return """
<Interchange_Baplie>
  <InterchangeHeader>
    <InterchangeControlRef>2023-02-23 15:02:10</InterchangeControlRef>
    <InterchangeRecipient>HPUK</InterchangeRecipient>
    <InterchangeSender>LER</InterchangeSender>
    <PreparationDateTime>2023-02-23 15:02:10</PreparationDateTime>
    <SyntaxId>
      <SyntaxIdCoded>IBP</SyntaxIdCoded>
    </SyntaxId>
  </InterchangeHeader>
  <MessageList>
    <Message>
      <EquipmentAndGoodsInfoList>
        <EquipmentAndGoodsInfo>
          <EquipmentInfoList>
            <EquipmentInfo>
              <EquipmentDtl>
                <EquipmentId>
                  <ContainerNum>ICIF02230001</ContainerNum>
                </EquipmentId>
                <EquipmentSizeType>2000</EquipmentSizeType>
                <FullEmptyInd>F</FullEmptyInd>
              </EquipmentDtl>
              <NameAndAddress>
                <PartyInfo>
                  <PartyInfo_BIC>LER</PartyInfo_BIC>
                </PartyInfo>
              </NameAndAddress>
            </EquipmentInfo>
          </EquipmentInfoList>
          <LocationId>
            <Location>
              <Location_ZZZ>
                <DischargePort_ZZZ>GBFXT</DischargePort_ZZZ>
                <FinalDestination_ZZZ>GBFXT</FinalDestination_ZZZ>
                <LoadingPort_ZZZ>HKHKG</LoadingPort_ZZZ>
              </Location_ZZZ>
            </Location>
          </LocationId>
          <Measurement>
            <Measurement_KGM>
              <GrossWeight_KGM>2500</GrossWeight_KGM>
              <VgmIndicator>Y</VgmIndicator>
            </Measurement_KGM>
          </Measurement>
          <StowageId>
            <StowageCell_ISO>010182</StowageCell_ISO>
          </StowageId>
        </EquipmentAndGoodsInfo>
      </EquipmentAndGoodsInfoList>
      <Header>
        <BeginningMessage>
          <DocumentId>4</DocumentId>
          <MessageFunction>9</MessageFunction>
        </BeginningMessage>
        <DateTimeInfo>
          <DateTime>
            <DocumentDateTime>2023-02-23 15:02:10</DocumentDateTime>
          </DateTime>
        </DateTimeInfo>
        <MessageHeader>
          <MessageId>
            <AssociationAssignedCode>SMDG22</AssociationAssignedCode>
            <ControllingAgency>UN</ControllingAgency>
            <MessageTypeId>BAPLIE</MessageTypeId>
            <MessageTypeRelNum>95B</MessageTypeRelNum>
            <MessageTypeVerNum>D</MessageTypeVerNum>
          </MessageId>
          <MessageRefNum>4</MessageRefNum>
        </MessageHeader>
      </Header>
      <Trailer>
        <MessageTrailer>
          <MessageRefNum>LER</MessageRefNum>
          <SegmentNum>50</SegmentNum>
        </MessageTrailer>
      </Trailer>
      <TransportInfoList>
        <TransportInfo>
          <LocationGroupInfo>
            <DateTimeInfo>
              <DateTime>
                <TransportDateTime>
                  <ArrivalTimeEst>20-- ::00</ArrivalTimeEst>
                  <DepartureTimeEst>20-- ::00</DepartureTimeEst>
                </TransportDateTime>
              </DateTime>
            </DateTimeInfo>
            <LocationId>
              <Location>
                <Location_ZZZ>
                  <DeparturePort_ZZZ>HKHKG</DeparturePort_ZZZ>
                  <NextPortCall_ZZZ>GBFXT</NextPortCall_ZZZ>
                </Location_ZZZ>
              </Location>
            </LocationId>
          </LocationGroupInfo>
          <TransportDtl>
            <LineVoyId>90345</LineVoyId>
            <TransportId>
              <TransportIdCoded>
                <CallSign>LER</CallSign>
              </TransportIdCoded>
              <TransportName>EmulationRunIssac</TransportName>
            </TransportId>
          </TransportDtl>
        </TransportInfo>
      </TransportInfoList>
    </Message>
  </MessageList>
</Interchange_Baplie>

    """


if __name__ == "__main__":
    # "D:\90798\Issac\repo\python-integrated-test\helper\generate_jms\data\baplie_tmp.xml"
    # python -m helper.jms.producer
    producer = Producer(
        "t3://icaveiut1.hphit.hutchisonports.com:30152",
        "jms/sp/InboundBayplanQueue",  # Bayplan
        # "jms/sp/MovinMaskPlanQueue",  # Movins
    )
    # producer.send_message(producer.sample_message)  # This works, able to find result in nGen
    cur_path = os.path.dirname(os.path.abspath(__file__))
    # get parent dir of cur_path
    cur_dir = os.path.dirname(cur_path)

    jms_path = os.path.join(cur_dir, "generate_jms", "data", "baplie_tmp.xml")
    # jms_path = os.path.join(cur_dir, "generate_jms", "data", "movins_tmp.xml")
    with open(jms_path, "r") as file:
        msg = file.read()
    producer.send_message(msg)
    print(f"{producer.queue} sent")
    print(f"{msg}")
    print("Done")
