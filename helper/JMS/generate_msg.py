import csv
import xml.etree.ElementTree as ET


def generate_message(csv_file):
    # Read the CSV file
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Create the root element
    root = ET.Element('Interchange_Baplie')

    # Add InterchangeHeader (static)
    interchange_header = ET.SubElement(root, 'InterchangeHeader')
    ET.SubElement(interchange_header, 'InterchangeControlRef').text = '2024-08-10 10:22:00'
    ET.SubElement(interchange_header, 'InterchangeRecipient').text = 'AQCT'
    ET.SubElement(interchange_header, 'InterchangeSender').text = 'NVD'
    ET.SubElement(interchange_header, 'PreparationDateTime').text = '2024-08-10 10:22:00'
    syntax_id = ET.SubElement(interchange_header, 'SyntaxId')
    ET.SubElement(syntax_id, 'SyntaxIdCoded').text = 'IBP'

    # Add MessageList
    message_list = ET.SubElement(root, 'MessageList')
    message = ET.SubElement(message_list, 'Message')

    # Add Header (static)
    header = ET.SubElement(message, 'Header')
    beginning_message = ET.SubElement(header, 'BeginningMessage')
    ET.SubElement(beginning_message, 'DocumentId').text = '36'
    ET.SubElement(beginning_message, 'MessageFunction').text = '9'
    date_time_info = ET.SubElement(header, 'DateTimeInfo')
    date_time = ET.SubElement(date_time_info, 'DateTime')
    ET.SubElement(date_time, 'DocumentDateTime').text = '2023-10-12 00:00:00'
    message_header = ET.SubElement(header, 'MessageHeader')
    message_id = ET.SubElement(message_header, 'MessageId')
    ET.SubElement(message_id, 'AssociationAssignedCode').text = 'SMDG22'
    ET.SubElement(message_id, 'ControllingAgency').text = 'UN'
    ET.SubElement(message_id, 'MessageTypeId').text = 'BAPLIE'
    ET.SubElement(message_id, 'MessageTypeRelNum').text = '95B'
    ET.SubElement(message_id, 'MessageTypeVerNum').text = 'D'
    ET.SubElement(message_header, 'MessageRefNum').text = '36'

    # Add Trailer (static)
    trailer = ET.SubElement(message, 'Trailer')
    message_trailer = ET.SubElement(trailer, 'MessageTrailer')
    ET.SubElement(message_trailer, 'MessageRefNum').text = 'NVD'
    ET.SubElement(message_trailer, 'SegmentNum').text = '50'

    # Add TransportInfoList (static)
    transport_info_list = ET.SubElement(message, 'TransportInfoList')
    transport_info = ET.SubElement(transport_info_list, 'TransportInfo')
    location_group_info = ET.SubElement(transport_info, 'LocationGroupInfo')
    date_time_info = ET.SubElement(location_group_info, 'DateTimeInfo')
    date_time = ET.SubElement(date_time_info, 'DateTime')
    transport_date_time = ET.SubElement(date_time, 'TransportDateTime')
    ET.SubElement(transport_date_time, 'ArrivalTimeEst').text = '2024-12-03 10:00:00'
    ET.SubElement(transport_date_time, 'DepartureTimeEst').text = '2024-12-04 11:30:00'
    location_id = ET.SubElement(location_group_info, 'LocationId')
    location = ET.SubElement(location_id, 'Location')
    location_zzz = ET.SubElement(location, 'Location_ZZZ')
    ET.SubElement(location_zzz, 'DeparturePort_ZZZ').text = 'SGSIN'
    ET.SubElement(location_zzz, 'NextPortCall_ZZZ').text = 'EGAKI'
    transport_dtl = ET.SubElement(transport_info, 'TransportDtl')
    ET.SubElement(transport_dtl, 'LineVoyId').text = 'V01'
    transport_id = ET.SubElement(transport_dtl, 'TransportId')
    transport_id_coded = ET.SubElement(transport_id, 'TransportIdCoded')
    ET.SubElement(transport_id_coded, 'CallSign').text = 'TSHM04'
    ET.SubElement(transport_id, 'TransportName').text = 'TSHM04'

    # Add EquipmentAndGoodsInfoList (dynamic)
    equipment_and_goods_info_list = ET.SubElement(message, 'EquipmentAndGoodsInfoList')
    for row in rows:
        if row['ContainerNum'].strip():
            equipment_and_goods_info = ET.SubElement(equipment_and_goods_info_list, 'EquipmentAndGoodsInfo')

            # EquipmentInfoList
            equipment_info_list = ET.SubElement(equipment_and_goods_info, 'EquipmentInfoList')
            equipment_info = ET.SubElement(equipment_info_list, 'EquipmentInfo')
            equipment_dtl = ET.SubElement(equipment_info, 'EquipmentDtl')
            equipment_id = ET.SubElement(equipment_dtl, 'EquipmentId')
            ET.SubElement(equipment_id, 'ContainerNum').text = row['ContainerNum']
            ET.SubElement(equipment_dtl, 'EquipmentSizeType').text = row['EquipmentSizeType']
            ET.SubElement(equipment_dtl, 'FullEmptyInd').text = row['FullEmptyInd']
            name_and_address = ET.SubElement(equipment_info, 'NameAndAddress')
            party_info = ET.SubElement(name_and_address, 'PartyInfo')
            ET.SubElement(party_info, 'PartyInfo_BIC').text = row['PartyInfo_BIC']

            # LocationId (static)
            location_id = ET.SubElement(equipment_and_goods_info, 'LocationId')
            location = ET.SubElement(location_id, 'Location')
            location_zzz = ET.SubElement(location, 'Location_ZZZ')
            ET.SubElement(location_zzz, 'DischargePort_ZZZ').text = 'EGAKI'
            ET.SubElement(location_zzz, 'LoadingPort_ZZZ').text = 'SGSIN'

            # Measurement (static)
            measurement = ET.SubElement(equipment_and_goods_info, 'Measurement')
            measurement_kgm = ET.SubElement(measurement, 'Measurement_KGM')
            ET.SubElement(measurement_kgm, 'GrossWeight_KGM').text = '8256'
            ET.SubElement(measurement_kgm, 'VgmIndicator').text = 'Y'

            # Dimension (static)
            dimension = ET.SubElement(equipment_and_goods_info, 'Dimension')
            ET.SubElement(dimension, 'Dimension_CMT')

            # StowageId (dynamic)
            stowage_id = ET.SubElement(equipment_and_goods_info, 'StowageId')
            ET.SubElement(stowage_id, 'StowageCell_ISO').text = str(row['StowageCell_ISO']).zfill(6)

    # Convert to string
    xml_str = ET.tostring(root, encoding='unicode')
    return xml_str

# Example usage
# message = generate_message('dc_data.csv')
# print(message)