"""
Tunneling module for PR-Agent webhook servers.

This module provides tunneling capabilities for local development, allowing webhook
servers to receive events from external services like GitHub, GitLab, etc.
"""

import json
import logging
import os
import subprocess
import time
from enum import Enum
from typing import Dict, Optional, Tuple, Union

from pr_agent.log import get_logger

logger = get_logger()


class TunnelService(str, Enum):
    """Supported tunneling services."""
    NGROK = "ngrok"
    LOCALTUNNEL = "localtunnel"


class TunnelManager:
    """
    Manages tunneling services for local webhook development.
    
    This class provides a unified interface for creating and managing tunnels
    using different tunneling services (ngrok, localtunnel). It handles automatic
    fallback if the preferred service fails.
    """
    
    def __init__(
        self,
        port: int = 3000,
        preferred_service: TunnelService = TunnelService.NGROK,
        auth_token: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """
        Initialize the tunnel manager.
        
        Args:
            port: The local port to expose
            preferred_service: The preferred tunneling service
            auth_token: Authentication token for ngrok (if required)
            region: Region for localtunnel (if required)
        """
        self.port = port
        self.preferred_service = preferred_service
        self.auth_token = auth_token
        self.region = region
        self.tunnel_url = None
        self.process = None
        
    def start_tunnel(self) -> str:
        """
        Start a tunnel using the preferred service with fallback.
        
        Returns:
            The public URL of the tunnel
            
        Raises:
            RuntimeError: If all tunneling services fail
        """
        logger.info(f"Starting tunnel with {self.preferred_service} (port: {self.port})")
        
        if self.preferred_service == TunnelService.NGROK:
            success, url = self._start_ngrok()
            if not success:
                logger.warning("Failed to start ngrok, falling back to localtunnel")
                success, url = self._start_localtunnel()
        else:
            success, url = self._start_localtunnel()
            if not success:
                logger.warning("Failed to start localtunnel, falling back to ngrok")
                success, url = self._start_ngrok()
                
        if not success:
            raise RuntimeError("Failed to start any tunneling service")
            
        self.tunnel_url = url
        logger.info(f"Tunnel established: {url}")
        return url
        
    def _start_ngrok(self) -> Tuple[bool, Optional[str]]:
        """
        Start an ngrok tunnel.
        
        Returns:
            A tuple of (success, url) where success is a boolean indicating if
            the tunnel was successfully created, and url is the public URL of
            the tunnel (or None if unsuccessful).
        """
        try:
            # Check if ngrok is installed
            try:
                subprocess.run(["ngrok", "--version"], check=True, capture_output=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.error("ngrok is not installed or not in PATH")
                return False, None
                
            # Start ngrok process
            cmd = ["ngrok", "http", str(self.port)]
            if self.auth_token:
                # Authenticate first if token is provided
                auth_process = subprocess.run(
                    ["ngrok", "authtoken", self.auth_token],
                    check=True,
                    capture_output=True
                )
                
            # Start the tunnel
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for tunnel to be established
            time.sleep(2)
            
            # Get the tunnel URL from the ngrok API
            api_url = "http://localhost:4040/api/tunnels"
            curl_process = subprocess.run(
                ["curl", "-s", api_url],
                check=True,
                capture_output=True,
                text=True
            )
            
            tunnels = json.loads(curl_process.stdout)
            if not tunnels.get("tunnels"):
                logger.error("No tunnels found in ngrok API response")
                return False, None
                
            # Get the HTTPS URL
            for tunnel in tunnels["tunnels"]:
                if tunnel["proto"] == "https":
                    return True, tunnel["public_url"]
                    
            logger.error("No HTTPS tunnel found in ngrok API response")
            return False, None
            
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            if self.process:
                self.process.terminate()
                self.process = None
            return False, None
            
    def _start_localtunnel(self) -> Tuple[bool, Optional[str]]:
        """
        Start a localtunnel tunnel.
        
        Returns:
            A tuple of (success, url) where success is a boolean indicating if
            the tunnel was successfully created, and url is the public URL of
            the tunnel (or None if unsuccessful).
        """
        try:
            # Check if localtunnel is installed
            try:
                subprocess.run(["lt", "--version"], check=True, capture_output=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                # Try with npx
                try:
                    subprocess.run(["npx", "localtunnel", "--version"], check=True, capture_output=True)
                except (subprocess.SubprocessError, FileNotFoundError):
                    logger.error("localtunnel is not installed or not in PATH")
                    return False, None
                    
            # Start localtunnel process
            cmd = ["lt", "--port", str(self.port)]
            if self.region:
                cmd.extend(["--subdomain", self.region])
                
            # If npx is needed
            if subprocess.run(["which", "lt"], capture_output=True).returncode != 0:
                cmd = ["npx", "localtunnel"] + cmd[1:]
                
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel to be established and get the URL
            for _ in range(10):  # Try for up to 10 seconds
                line = self.process.stdout.readline().strip()
                if "your url is:" in line.lower():
                    url = line.split("your url is:")[1].strip()
                    return True, url
                time.sleep(1)
                
            logger.error("Failed to get localtunnel URL")
            return False, None
            
        except Exception as e:
            logger.error(f"Failed to start localtunnel: {e}")
            if self.process:
                self.process.terminate()
                self.process = None
            return False, None
            
    def stop_tunnel(self) -> None:
        """Stop the active tunnel."""
        if self.process:
            logger.info(f"Stopping tunnel: {self.tunnel_url}")
            self.process.terminate()
            self.process = None
        self.tunnel_url = None


def create_tunnel(
    port: int = 3000,
    service: Union[str, TunnelService] = TunnelService.NGROK,
    auth_token: Optional[str] = None,
    region: Optional[str] = None,
) -> str:
    """
    Create a tunnel for the specified port.
    
    This is a convenience function that creates a TunnelManager and starts a tunnel.
    
    Args:
        port: The local port to expose
        service: The tunneling service to use
        auth_token: Authentication token for ngrok (if required)
        region: Region for localtunnel (if required)
        
    Returns:
        The public URL of the tunnel
        
    Raises:
        RuntimeError: If all tunneling services fail
    """
    if isinstance(service, str):
        service = TunnelService(service)
        
    # Check for environment variables
    auth_token = auth_token or os.environ.get("TUNNEL_AUTH_TOKEN")
    region = region or os.environ.get("TUNNEL_REGION")
    
    manager = TunnelManager(
        port=port,
        preferred_service=service,
        auth_token=auth_token,
        region=region,
    )
    
    return manager.start_tunnel()

