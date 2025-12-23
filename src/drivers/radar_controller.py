"""
EchoGuard Radar Controller
Handles radar initialization, configuration, and control commands
"""

import socket
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RadarController:
    """Controls EchoGuard radar via telnet command port"""
    
    def __init__(self, host: str, port: int = 23, timeout: float = 10.0):
        """
        Initialize radar controller
        
        Args:
            host: Radar IP address
            port: Command port (default: 23)
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to radar command port
        
        Returns:
            True if connected successfully
        """
        try:
            logger.info(f"Connecting to radar at {self.host}:{self.port}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.connected = True
            
            # Clear any initial messages (non-blocking)
            self.sock.setblocking(False)
            try:
                self.sock.recv(4096)
            except (socket.timeout, BlockingIOError):
                pass
            self.sock.setblocking(True)
            
            logger.info("Connected to radar command port")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to radar: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from radar"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False
        logger.info("Disconnected from radar")
    
    def is_online(self) -> bool:
        """Check if radar is connected and online"""
        return self.connected
    
    def _send_command(self, command: str, timeout: float = 1.0) -> str:
        """
        Send command to radar and get response
        
        Args:
            command: Command string to send
            timeout: Response timeout in seconds
            
        Returns:
            Response string from radar
        """
        if not self.connected:
            logger.error("Not connected to radar")
            return ""
        
        try:
            # Send command with CRLF termination (required by radar)
            self.sock.sendall((command + "\r\n").encode('ascii'))
            logger.debug(f"Sent: {command}")
            
            # Wait for response
            self.sock.settimeout(timeout)
            response = self.sock.recv(8192).decode('ascii', errors='ignore')
            logger.debug(f"Received: {response}")
            
            return response.strip()
            
        except socket.timeout:
            logger.error(f"Timeout waiting for response to: {command}")
            return ""
        except Exception as e:
            logger.error(f"Error sending command '{command}': {e}")
            return ""
    
    def send_command(self, command: str, wait: float = 0.1) -> str:
        """
        Public method to send command to radar
        
        Args:
            command: Command string to send
            wait: Time to wait after sending (seconds)
            
        Returns:
            Response string from radar
        """
        response = self._send_command(command)
        if wait > 0:
            time.sleep(wait)
        return response
    
    def initialize_radar(self) -> bool:
        """
        Initialize radar with standard startup sequence
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing radar...")
            
            # Stop any running modes
            logger.debug("Stopping any active modes...")
            self.send_command("MODE:SWT:STOP")
            self.send_command("MODE:SEARCH:STOP")
            
            # Get radar identification
            logger.debug("Querying radar identification...")
            response = self.send_command("*IDN?", wait=0.1)
            logger.info(f"Radar ID: {response[:100]}")
            
            # Check built-in test status
            logger.debug("Checking BIT status...")
            response = self.send_command("*TST?", wait=0.1)
            if "CURRENT STATE: SYSTEM_STATE_STANDBY" in response or "OK" in response:
                logger.info("Radar BIT passed")
            else:
                logger.warning(f"Radar BIT status: {response[:200]}")
            
            # Reset system time
            logger.debug("Resetting system time...")
            self.send_command("SYS:TIME 0,0")
            
            # Reset parameters to factory defaults
            logger.debug("Resetting parameters to factory defaults...")
            response = self.send_command("RESET:PARAMETERS", wait=0.1)
            if "OK" in response:
                logger.info("Parameters reset to factory defaults")
            
            logger.info("Radar initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Radar initialization failed: {e}")
            return False
    
    def configure_radar(self, config: Dict[str, Any]) -> bool:
        """
        Configure radar parameters
        
        Args:
            config: Configuration dictionary with radar parameters
            
        Returns:
            True if configuration successful
        """
        try:
            logger.info("Configuring radar...")
            
            # Set operation mode (0=Pedestrian, 1=UAS, 2=Plane)
            mode = config.get('operation_mode', 1)
            logger.debug(f"Setting operation mode to {mode} (UAS)")
            self.send_command(f"MODE:SWT:OPERATIONMODE {mode}")
            
            # Set search FOV
            search_az_min = config.get('search_az_min', -60)
            search_az_max = config.get('search_az_max', 60)
            search_el_min = config.get('search_el_min', -40)
            search_el_max = config.get('search_el_max', 40)
            
            logger.debug(f"Setting search FOV: Az[{search_az_min},{search_az_max}], El[{search_el_min},{search_el_max}]")
            self.send_command(f"MODE:SWT:SEARCH:AZFOVMIN {search_az_min}")
            self.send_command(f"MODE:SWT:SEARCH:AZFOVMAX {search_az_max}")
            
            self.send_command(f"MODE:SWT:SEARCH:ELFOVMIN {search_el_min}")
            self.send_command(f"MODE:SWT:SEARCH:ELFOVMAX {search_el_max}")
            
            # Set track FOV
            track_az_min = config.get('track_az_min', -60)
            track_az_max = config.get('track_az_max', 60)
            track_el_min = config.get('track_el_min', -40)
            track_el_max = config.get('track_el_max', 40)
            
            logger.debug(f"Setting track FOV: Az[{track_az_min},{track_az_max}], El[{track_el_min},{track_el_max}]")
            self.send_command(f"MODE:SWT:TRACK:AZFOVMIN {track_az_min}")
            self.send_command(f"MODE:SWT:TRACK:AZFOVMAX {track_az_max}")
            self.send_command(f"MODE:SWT:TRACK:ELFOVMIN {track_el_min}")
            self.send_command(f"MODE:SWT:TRACK:ELFOVMAX {track_el_max}")
            
            # Set platform orientation if provided
            if 'platform_heading' in config or 'platform_pitch' in config or 'platform_roll' in config:
                heading = config.get('platform_heading', 0.0)
                pitch = config.get('platform_pitch', 0.0)
                roll = config.get('platform_roll', 0.0)
                logger.debug(f"Setting platform orientation: H={heading}, P={pitch}, R={roll}")
                # Note: This requires superuser password, skip for now
                # self.send_command(f"PLATFORM:STATE:ORIENTATION <password> {heading}, {pitch}, {roll}")
            
            logger.info("Radar configuration complete")
            return True
            
        except Exception as e:
            logger.error(f"Radar configuration failed: {e}")
            return False
    
    def start_radar(self) -> bool:
        """
        Start radar in Search-While-Track mode
        
        Returns:
            True if radar started successfully
        """
        try:
            logger.info("Starting radar in Search-While-Track mode...")
            response = self.send_command("MODE:SWT:START", wait=0.1)
            
            if "OK" in response:
                logger.info("Radar started successfully - now streaming data")
                return True
            else:
                logger.error(f"Failed to start radar: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start radar: {e}")
            return False
    
    def stop_radar(self) -> bool:
        """
        Stop radar scanning
        
        Returns:
            True if radar stopped successfully
        """
        try:
            logger.info("Stopping radar...")
            response = self.send_command("MODE:SWT:STOP", wait=0.1)
            
            if "OK" in response or "Command Not Available" in response:
                logger.info("Radar stopped")
                return True
            else:
                logger.warning(f"Stop command response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop radar: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get radar status
        
        Returns:
            Dictionary with radar status information
        """
        try:
            response = self.send_command("*TST?", wait=0.1)
            
            status = {
                'connected': self.connected,
                'response': response
            }
            
            # Parse state from response
            if "CURRENT STATE:" in response:
                for line in response.split('\n'):
                    if "CURRENT STATE:" in line:
                        state = line.split(':')[1].strip()
                        status['state'] = state
                        break
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get radar status: {e}")
            return {'connected': self.connected, 'error': str(e)}
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Query radar for current configuration settings
        
        Returns:
            Dictionary with current radar configuration
        """
        if not self.connected:
            logger.warning("Cannot get configuration - not connected")
            return {}
        
        try:
            logger.info("Querying radar configuration...")
            config = {}
            
            # Query operation mode
            response = self.send_command("MODE:SWT:OPERATIONMODE?", wait=0.1)
            if response:
                try:
                    config['operation_mode'] = int(response.strip())
                except:
                    config['operation_mode'] = 1
            
            # Query search FOV
            response = self.send_command("MODE:SWT:SEARCH:AZFOVMIN?", wait=0.1)
            if response and "Command Not Available" not in response:
                try:
                    config['search_az_min'] = int(float(response.strip()))
                except Exception as e:
                    logger.debug(f"Failed to parse AZFOVMIN: {e}")
                    config['search_az_min'] = -60
            else:
                logger.debug("Cannot query FOV while streaming")
                return {}  # Return empty dict to signal verification is not possible
            
            response = self.send_command("MODE:SWT:SEARCH:AZFOVMAX?", wait=0.1)
            if response:
                try:
                    config['search_az_max'] = int(float(response.strip()))
                except:
                    config['search_az_max'] = 60
            
            response = self.send_command("MODE:SWT:SEARCH:ELFOVMIN?", wait=0.1)
            if response:
                try:
                    config['search_el_min'] = int(float(response.strip()))
                except:
                    config['search_el_min'] = -40
            
            response = self.send_command("MODE:SWT:SEARCH:ELFOVMAX?", wait=0.1)
            if response:
                try:
                    config['search_el_max'] = int(float(response.strip()))
                except:
                    config['search_el_max'] = 40
            
            # Query track FOV
            response = self.send_command("MODE:SWT:TRACK:AZFOVMIN?", wait=0.1)
            if response:
                try:
                    config['track_az_min'] = int(float(response.strip()))
                except:
                    config['track_az_min'] = -60
            
            response = self.send_command("MODE:SWT:TRACK:AZFOVMAX?", wait=0.1)
            if response:
                try:
                    config['track_az_max'] = int(float(response.strip()))
                except:
                    config['track_az_max'] = 60
            
            response = self.send_command("MODE:SWT:TRACK:ELFOVMIN?", wait=0.1)
            if response:
                try:
                    config['track_el_min'] = int(float(response.strip()))
                except:
                    config['track_el_min'] = -40
            
            response = self.send_command("MODE:SWT:TRACK:ELFOVMAX?", wait=0.1)
            if response:
                try:
                    config['track_el_max'] = int(float(response.strip()))
                except:
                    config['track_el_max'] = 40
            
            logger.info(f"Retrieved radar configuration: {config}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to get radar configuration: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_radar()
        self.disconnect()
