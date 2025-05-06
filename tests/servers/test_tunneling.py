"""
Tests for the tunneling module.
"""

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from pr_agent.servers.tunneling import TunnelManager, TunnelService, create_tunnel


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing."""
    with patch("pr_agent.servers.tunneling.subprocess") as mock_subprocess:
        # Mock successful version check
        version_process = MagicMock()
        version_process.returncode = 0
        mock_subprocess.run.return_value = version_process
        
        # Mock successful curl response for ngrok
        curl_process = MagicMock()
        curl_process.stdout = json.dumps({
            "tunnels": [
                {
                    "name": "command_line",
                    "uri": "/api/tunnels/command_line",
                    "public_url": "https://test-ngrok.io",
                    "proto": "https",
                    "config": {"addr": "http://localhost:3000", "inspect": True},
                    "metrics": {
                        "conns": {"count": 0, "gauge": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0},
                        "http": {"count": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}
                    }
                }
            ]
        })
        mock_subprocess.run.return_value = curl_process
        
        # Mock Popen for process management
        mock_process = MagicMock()
        mock_process.stdout.readline.return_value = "your url is: https://test-localtunnel.me"
        mock_subprocess.Popen.return_value = mock_process
        
        yield mock_subprocess


def test_ngrok_tunnel_start(mock_subprocess):
    """Test starting an ngrok tunnel."""
    manager = TunnelManager(preferred_service=TunnelService.NGROK)
    url = manager.start_tunnel()
    
    assert url == "https://test-ngrok.io"
    assert manager.tunnel_url == "https://test-ngrok.io"
    
    # Check that ngrok was called correctly
    mock_subprocess.run.assert_any_call(
        ["ngrok", "--version"],
        check=True,
        capture_output=True
    )
    
    mock_subprocess.Popen.assert_called_with(
        ["ngrok", "http", "3000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    mock_subprocess.run.assert_any_call(
        ["curl", "-s", "http://localhost:4040/api/tunnels"],
        check=True,
        capture_output=True,
        text=True
    )


def test_localtunnel_start(mock_subprocess):
    """Test starting a localtunnel tunnel."""
    # Mock which command to simulate lt not being in PATH
    which_process = MagicMock()
    which_process.returncode = 1
    mock_subprocess.run.side_effect = [
        which_process,  # which lt
        mock_subprocess.run.return_value,  # npx localtunnel --version
        mock_subprocess.run.return_value,  # curl
    ]
    
    manager = TunnelManager(preferred_service=TunnelService.LOCALTUNNEL)
    url = manager.start_tunnel()
    
    assert url == "https://test-localtunnel.me"
    assert manager.tunnel_url == "https://test-localtunnel.me"
    
    # Check that npx localtunnel was called correctly
    mock_subprocess.Popen.assert_called_with(
        ["npx", "localtunnel", "--port", "3000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def test_ngrok_fallback_to_localtunnel(mock_subprocess):
    """Test fallback from ngrok to localtunnel."""
    # Make ngrok fail
    mock_subprocess.run.side_effect = subprocess.SubprocessError("ngrok failed")
    
    # But make localtunnel succeed
    mock_process = MagicMock()
    mock_process.stdout.readline.return_value = "your url is: https://test-localtunnel.me"
    mock_subprocess.Popen.return_value = mock_process
    
    # Reset side_effect after first call
    def side_effect(*args, **kwargs):
        mock_subprocess.run.side_effect = None
        raise subprocess.SubprocessError("ngrok failed")
    
    mock_subprocess.run.side_effect = side_effect
    
    manager = TunnelManager(preferred_service=TunnelService.NGROK)
    url = manager.start_tunnel()
    
    assert url == "https://test-localtunnel.me"
    assert manager.tunnel_url == "https://test-localtunnel.me"


def test_stop_tunnel(mock_subprocess):
    """Test stopping a tunnel."""
    manager = TunnelManager()
    url = manager.start_tunnel()
    
    assert manager.process is not None
    
    manager.stop_tunnel()
    
    assert manager.process is None
    assert manager.tunnel_url is None
    manager.process.terminate.assert_called_once()


def test_create_tunnel_helper(mock_subprocess):
    """Test the create_tunnel helper function."""
    with patch("pr_agent.servers.tunneling.TunnelManager") as mock_manager_class:
        mock_manager = MagicMock()
        mock_manager.start_tunnel.return_value = "https://test-helper.io"
        mock_manager_class.return_value = mock_manager
        
        url = create_tunnel(
            port=8080,
            service="ngrok",
            auth_token="test-token",
            region="us"
        )
        
        assert url == "https://test-helper.io"
        mock_manager_class.assert_called_with(
            port=8080,
            preferred_service=TunnelService.NGROK,
            auth_token="test-token",
            region="us"
        )
        mock_manager.start_tunnel.assert_called_once()

