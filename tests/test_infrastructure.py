"""Quick validation test to ensure test infrastructure works."""
import pytest


class TestInfrastructure:
    """Basic tests to validate test setup."""

    @pytest.mark.unit
    def test_pytest_works(self):
        """Verify pytest is working."""
        assert True

    @pytest.mark.unit
    def test_fixtures_available(self, mock_openremote_client, mock_mcp_client):
        """Verify fixtures are available."""
        assert mock_openremote_client is not None
        assert mock_mcp_client is not None

    @pytest.mark.unit
    def test_sample_data_fixtures(self, sample_asset, sample_ruleset):
        """Verify sample data fixtures work."""
        assert sample_asset["id"] == "test-asset-123"
        assert sample_ruleset["id"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_async_works(self):
        """Verify async tests work."""
        async def dummy_async():
            return "success"
        
        result = await dummy_async()
        assert result == "success"
