"""Tests for shared module - OpenRemote service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import HTTPStatusError, Response

from shared.openremote_service import (
    OpenRemoteService,
    get_openremote_service,
    init_openremote_service,
)
from openremote_client.schemas import ExternalServiceSchema


class TestOpenRemoteService:
    """Test cases for OpenRemoteService class."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_register_success(self, mock_openremote_client):
        """Test successful service registration."""
        service_schema = ExternalServiceSchema(
            serviceId="test-service",
            label="Test Service",
            homepageUrl="http://test",
            status="AVAILABLE"
        )
        
        service = await OpenRemoteService.register(
            mock_openremote_client,
            service_schema,
            heartbeat_interval=30
        )
        
        assert service is not None
        assert service.service_id == "test-service"
        assert service.instance_id == 123
        assert service.client == mock_openremote_client
        mock_openremote_client.services.register_service.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_register_failure(self, mock_openremote_client):
        """Test failed service registration."""
        mock_openremote_client.services.register_service = AsyncMock(
            side_effect=Exception("Connection failed")
        )
        
        service_schema = ExternalServiceSchema(
            serviceId="test-service",
            label="Test Service",
            homepageUrl="http://test",
            status="AVAILABLE"
        )
        
        with pytest.raises(RuntimeError, match="Failed to connect to OpenRemote"):
            await OpenRemoteService.register(
                mock_openremote_client,
                service_schema
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_send_heartbeat(self, mock_openremote_client):
        """Test heartbeat sending."""
        service_schema = ExternalServiceSchema(
            serviceId="test-service",
            label="Test Service",
            homepageUrl="http://test",
            status="AVAILABLE"
        )
        
        service = await OpenRemoteService.register(
            mock_openremote_client,
            service_schema
        )
        
        await service.send_heartbeat()
        
        mock_openremote_client.services.heartbeat.assert_called_once_with(
            "test-service", 123
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_deregister(self, mock_openremote_client):
        """Test service deregistration."""
        service_schema = ExternalServiceSchema(
            serviceId="test-service",
            label="Test Service",
            homepageUrl="http://test",
            status="AVAILABLE"
        )
        
        service = await OpenRemoteService.register(
            mock_openremote_client,
            service_schema
        )
        
        await service.deregister()
        
        mock_openremote_client.services.deregister_service.assert_called_once_with(
            "test-service", 123
        )


class TestOpenRemoteServiceGlobal:
    """Test global service management functions."""

    @pytest.mark.unit
    def test_get_openremote_service_not_initialized(self):
        """Test get_openremote_service raises error when not initialized."""
        # Need to reset the global variable
        import shared.openremote_service as or_service
        or_service._OpenRemoteService__openremote_service = None
        
        with pytest.raises(RuntimeError, match="OpenRemote service not initialized"):
            get_openremote_service()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_init_openremote_service(self, mock_openremote_client):
        """Test init_openremote_service function."""
        service_schema = ExternalServiceSchema(
            serviceId="test-service",
            label="Test Service",
            homepageUrl="http://test",
            status="AVAILABLE"
        )
        
        with patch('shared.openremote_service.OpenRemoteClient', return_value=mock_openremote_client):
            await init_openremote_service(
                service_schema=service_schema,
                host="http://localhost:8080",
                client_id="test-client",
                client_secret="test-secret",
                verify_SSL=False
            )
            
            service = get_openremote_service()
            assert service is not None
            assert service.service_id == "test-service"
