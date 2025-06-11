#!/usr/bin/env python3
"""
Appointment HTTP Service
Handles sending AppointmentCreateUpdate messages with authentication and saving responses as XML files.
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from helper.logger import logger
from helper.paths import ProjectPaths
import base64

class AppointmentMessageSender:
    """
    HTTP Message Sender for AppointmentCreateUpdate messages with authentication and response saving.
    """
    
    def __init__(self, 
                 endpoint_url: str = "https://aqctiut1.hphit.hutchisonports.com:30154/services/message/tasService",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 save_directory: Optional[Union[str, Path]] = None):
        """
        Initialize the appointment message sender.
        
        Args:
            endpoint_url: The HTTP endpoint URL to send messages to
            username: Username for authentication
            password: Password for authentication
            save_directory: Directory to save response XML files (defaults to project responses directory)
        """
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        self.save_directory = Path(save_directory) if save_directory else ProjectPaths.RESPONSES
        
        # Create save directory if it doesn't exist
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # Setup session with headers
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/xml',
            'Accept': 'application/xml',
            'User-Agent': 'Appointment-Sender/1.0'
        }
        
        # Add authentication if provided
        if self.username and self.password:
            self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication for the HTTP session."""
        if self.username and self.password:
            # Basic Authentication
            auth_string = f"{self.username}:{self.password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            self.headers['Authorization'] = f'Basic {auth_b64}'
            
        self.session.headers.update(self.headers)
        logger.info(f"Authentication configured for user: {self.username}")
    
    def _generate_filename(self, message_name: str) -> str:
        """
        Generate filename based on current datetime and message name.
        
        Args:
            message_name: Name/identifier of the message
            
        Returns:
            Generated filename with timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        clean_message_name = "".join(c for c in message_name if c.isalnum() or c in ('-', '_'))
        return f"{timestamp}_{clean_message_name}.xml"
    
    def send_message(self, 
                    xml_message: str, 
                    message_name: str = "appointment") -> Dict[str, Any]:
        """
        Send XML message to the HTTP endpoint and save response.
        
        Args:
            xml_message: XML message to send
            message_name: Name identifier for the message (used in filename)
            
        Returns:
            Dictionary containing response information and file path
        """
        try:
            logger.info(f"Sending appointment message '{message_name}' to {self.endpoint_url}")
            logger.debug(f"Message content: {xml_message}")
            
            # Send the request
            response = self.session.post(
                self.endpoint_url,
                data=xml_message,
                timeout=30
            )
            
            # Generate filename for response
            response_filename = self._generate_filename(f"{message_name}_response")
            response_file_path = self.save_directory / response_filename
            
            # Save response as XML file
            self._save_response_as_xml(response, response_file_path, message_name)
            
            # Parse response to check for success/failure
            response_analysis = self._analyze_response(response.text)
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_text': response.text,
                'response_headers': dict(response.headers),
                'request_id': response.headers.get('X-Request-ID', 'N/A'),
                'response_file_path': str(response_file_path),
                'message_name': message_name,
                'timestamp': datetime.now().isoformat(),
                'appointment_status': response_analysis
            }
            
            if result['success']:
                logger.info(f"Message '{message_name}' sent successfully. Response saved to: {response_file_path}")
                if response_analysis.get('appointment_successful'):
                    logger.info(f"Appointment created/updated successfully for container: {response_analysis.get('container_id')}")
                else:
                    logger.warning(f"Appointment failed: {response_analysis.get('fail_reason', 'Unknown reason')}")
            else:
                logger.error(f"Failed to send message '{message_name}'. Status: {response.status_code}")
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout while sending message '{message_name}'")
            return {
                'success': False, 
                'error': 'Request timeout',
                'message_name': message_name,
                'timestamp': datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {self.endpoint_url} for message '{message_name}'")
            return {
                'success': False, 
                'error': 'Connection error',
                'message_name': message_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error while sending message '{message_name}': {e}")
            return {
                'success': False, 
                'error': str(e),
                'message_name': message_name,
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_response(self, response_text: str) -> Dict[str, Any]:
        """
        Analyze the AppointmentCreateUpdateReturn response.
        
        Args:
            response_text: XML response text
            
        Returns:
            Dictionary with response analysis
        """
        try:
            root = ET.fromstring(response_text)
            
            # Check return code
            return_code_elem = root.find('.//CommonResponse/returnCode')
            return_code = return_code_elem.text if return_code_elem is not None else 'Unknown'
            
            # Check container details
            container_elem = root.find('.//tasContainer')
            if container_elem is not None:
                cntr_id = container_elem.find('cntrId')
                valid_tas_cntr = container_elem.find('validTASCntr')
                fail_reason = container_elem.find('failReason')
                appointment_status = container_elem.find('appointmentStatus')
                
                return {
                    'return_code': return_code,
                    'container_id': cntr_id.text if cntr_id is not None else 'Unknown',
                    'valid_tas_container': valid_tas_cntr.text if valid_tas_cntr is not None else 'Unknown',
                    'appointment_successful': valid_tas_cntr.text == 'Y' if valid_tas_cntr is not None else False,
                    'fail_reason': fail_reason.text if fail_reason is not None else None,
                    'appointment_status': appointment_status.text if appointment_status is not None else None
                }
            
            return {
                'return_code': return_code,
                'appointment_successful': return_code == '000',
                'container_id': 'Unknown'
            }
            
        except ET.ParseError:
            return {
                'return_code': 'PARSE_ERROR',
                'appointment_successful': False,
                'error': 'Failed to parse XML response'
            }
    
    def _save_response_as_xml(self, response: requests.Response, file_path: Path, message_name: str):
        """
        Save HTTP response as XML file.
        
        Args:
            response: HTTP response object
            file_path: Path where to save the XML file
            message_name: Name of the message for metadata
        """
        try:
            # Try to parse and format the response XML
            response_xml = ET.fromstring(response.text)
            ET.indent(response_xml, space="  ", level=0)
            
            # Create a wrapper with metadata
            root = ET.Element('AppointmentResponse')
            
            # Add metadata
            metadata = ET.SubElement(root, 'Metadata')
            ET.SubElement(metadata, 'MessageName').text = message_name
            ET.SubElement(metadata, 'Timestamp').text = datetime.now().isoformat()
            ET.SubElement(metadata, 'StatusCode').text = str(response.status_code)
            ET.SubElement(metadata, 'URL').text = response.url
            
            # Add headers
            headers_elem = ET.SubElement(root, 'Headers')
            for key, value in response.headers.items():
                header_elem = ET.SubElement(headers_elem, 'Header')
                header_elem.set('name', key)
                header_elem.text = value
            
            # Add the actual response
            response_elem = ET.SubElement(root, 'ResponseBody')
            response_elem.append(response_xml)
            
            # Write to file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            
            with open(file_path, 'wb') as f:
                tree.write(f, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"Response saved to XML file: {file_path}")
            
        except ET.ParseError:
            # If response is not valid XML, save as plain text with metadata
            fallback_path = file_path.with_suffix('.txt')
            with open(fallback_path, 'w', encoding='utf-8') as f:
                f.write(f"Appointment Response for {message_name}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Status Code: {response.status_code}\n")
                f.write(f"Headers: {dict(response.headers)}\n")
                f.write(f"Body:\n{response.text}")
            logger.info(f"Response saved as text file (XML parse failed): {fallback_path}")
        except Exception as e:
            logger.error(f"Error saving response to XML: {e}")


class AppointmentMessageGenerator:
    """
    Message Generator for AppointmentCreateUpdate messages with dynamic fields.
    """
    
    def __init__(self):
        """Initialize the appointment message generator."""
        pass
    
    def generate_appointment_message(self, cntr_id: str, **kwargs) -> str:
        """
        Generate AppointmentCreateUpdate XML message with dynamic fields.
        
        Args:
            cntr_id: Container ID received from other class
            **kwargs: Additional fields to override defaults
            
        Returns:
            Generated XML message as string
        """
        # Generate dynamic fields
        fields = self._generate_dynamic_fields(cntr_id, **kwargs)
        
        # Create XML message
        xml_message = self._create_appointment_xml(fields)
        
        logger.info(f"Generated appointment message for container: {cntr_id}")
        return xml_message
    
    def _generate_dynamic_fields(self, cntr_id: str, **kwargs) -> Dict[str, str]:
        """
        Generate dynamic fields for the AppointmentCreateUpdate message.
        
        Args:
            cntr_id: Container ID from external source
            **kwargs: Override values for any field
            
        Returns:
            Dictionary containing all message fields
        """
        # Current date for appointment (YYYYMMDD format)
        current_date = datetime.now()
        appointment_date = kwargs.get('appointmentDate', current_date.strftime("%Y%m%d"))
        
        # Current hour + 1 for appointment time (just hour as string)
        appointment_hour = current_date.hour + 1
        if appointment_hour >= 24:
            appointment_hour = 0
        appointment_time = kwargs.get('appointmentTime', str(appointment_hour))
        
        # Default fields (can be overridden by kwargs)
        fields = {
            # Main identifiers
            'cntrId': cntr_id,
            'appointmentDate': appointment_date,
            'appointmentTime': appointment_time,
            
            # Fixed fields per your requirements
            'restrictSameTmlInd': kwargs.get('restrictSameTmlInd', 'N'),
            'requestSeparateTrans': kwargs.get('requestSeparateTrans', 'Y'),
            'actionCode': kwargs.get('actionCode', 'CREATE'),
            'mode': kwargs.get('mode', 'PI'),
            'bolNo': kwargs.get('bolNo', 'BL01'),
            'bookingNo': kwargs.get('bookingNo', ''),
            'terminalId': kwargs.get('terminalId', 'AQCT'),
            'gateNo': kwargs.get('gateNo', ''),
            'driverName': kwargs.get('driverName', ''),
            'driverLicenseNo': kwargs.get('driverLicenseNo', ''),
            'tractorNo': kwargs.get('tractorNo', ''),
            'tractorCompanyName': kwargs.get('tractorCompanyName', ''),
            'clearingAgentName': kwargs.get('clearingAgentName', ''),
            'clearingAgentRepName': kwargs.get('clearingAgentRepName', ''),
            'tictsId': kwargs.get('tictsId', ''),
            'sourcePoint': kwargs.get('sourcePoint', 'UBI'),
            'userId': kwargs.get('userId', 'oscar'),
            'vip': kwargs.get('vip', 'N'),
            'remark': kwargs.get('remark', '123')
        }
        
        # Apply any additional overrides
        fields.update(kwargs)
        
        return fields
    
    def _create_appointment_xml(self, fields: Dict[str, str]) -> str:
        """
        Create AppointmentCreateUpdate XML message using the provided fields.
        
        Args:
            fields: Dictionary of field values
            
        Returns:
            XML message as formatted string
        """
        # Create root element
        root = ET.Element('AppointmentCreateUpdate')
        
        # Add the three main elements in order
        restrict_elem = ET.SubElement(root, 'restrictSameTmlInd')
        restrict_elem.text = fields['restrictSameTmlInd']
        
        request_elem = ET.SubElement(root, 'requestSeparateTrans')
        request_elem.text = fields['requestSeparateTrans']
        
        # AppointmentChangeList
        change_list = ET.SubElement(root, 'AppointmentChangeList')
        
        # AppointmentChange
        change = ET.SubElement(change_list, 'AppointmentChange')
        
        # Add all fields in the order shown in the example
        field_order = [
            'actionCode', 'cntrId', 'mode', 'bolNo', 'bookingNo', 'terminalId',
            'appointmentDate', 'appointmentTime', 'gateNo', 'driverName',
            'driverLicenseNo', 'tractorNo', 'tractorCompanyName', 'clearingAgentName',
            'clearingAgentRepName', 'tictsId', 'sourcePoint', 'userId', 'vip', 'remark'
        ]
        
        for field_name in field_order:
            if field_name in fields:
                elem = ET.SubElement(change, field_name)
                elem.text = fields[field_name]
        
        # Format XML with proper indentation
        ET.indent(root, space="   ", level=0)  # Using 3 spaces as in the example
        
        # Convert to string with XML declaration
        xml_str = ET.tostring(root, encoding='unicode')
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'


class AppointmentService:
    """
    Complete Appointment Service combining sender and generator.
    """
    
    def __init__(self, 
                 endpoint_url: str = "http://172.18.51.25:20210/services/message/tasService",
                 username = os.environ.get('USER'),
                 password = os.environ.get('PASSWORD'),
                 save_directory: Optional[Union[str, Path]] = None):
        """
        Initialize the complete appointment service.
        
        Args:
            endpoint_url: HTTP endpoint URL
            username: Authentication username (if None, will try environment variables)
            password: Authentication password (if None, will try environment variables)
            save_directory: Directory to save response files (defaults to project responses directory)
        """
        self.sender = AppointmentMessageSender(endpoint_url, username, password, save_directory)
        self.generator = AppointmentMessageGenerator()
    
    def send_appointment_request(self, 
                               cntr_id: str, 
                               message_name: Optional[str] = None,
                               **kwargs) -> Dict[str, Any]:
        """
        Generate and send an appointment message in one operation.
        
        Args:
            cntr_id: Container ID for the appointment
            message_name: Name for the message (defaults to cntr_id)
            **kwargs: Additional field overrides
            
        Returns:
            Dictionary with generation and sending results
        """
        if message_name is None:
            message_name = f"appointment_{cntr_id}"
        
        # Generate message
        xml_message = self.generator.generate_appointment_message(cntr_id, **kwargs)
        
        # Send message and save response
        result = self.sender.send_message(xml_message, message_name)
        
        # Add generation info to result
        result['generated_message'] = xml_message
        result['cntr_id'] = cntr_id
        
        return result
    
    def set_credentials(self, username: str, password: str):
        """Update authentication credentials."""
        self.sender.username = username
        self.sender.password = password
        self.sender._setup_authentication()
    
    def create_appointment(self, cntr_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new appointment (actionCode=CREATE)."""
        kwargs['actionCode'] = 'CREATE'
        return self.send_appointment_request(cntr_id, **kwargs)
    
    def update_appointment(self, cntr_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing appointment (actionCode=UPDATE)."""
        kwargs['actionCode'] = 'UPDATE'
        return self.send_appointment_request(cntr_id, **kwargs)

if __name__ == "__main__":
    tas = AppointmentService()
    tas.create_appointment("TEST000210")