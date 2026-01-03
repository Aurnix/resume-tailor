"""
Backend tests for Resume Tailor API and core modules.
"""

import pytest
from fastapi.testclient import TestClient


class TestCoreImports:
    """Test that all core modules import correctly."""

    def test_import_config(self):
        from config import Config
        config = Config()
        assert hasattr(config, 'MODEL')
        assert hasattr(config, 'OUTPUT_DIR')

    def test_import_core_models(self):
        from core import (
            ParsedJobDescription,
            ParsedResume,
            ContactInfo,
            Role,
            Bullet,
            BulletMatch,
            FitAnalysis,
            TailoredContent,
        )
        # Verify classes exist
        assert ParsedJobDescription is not None
        assert ParsedResume is not None

    def test_import_jd_parser(self):
        from core.jd_parser import JobDescriptionParser
        assert JobDescriptionParser is not None

    def test_import_resume_analyzer(self):
        from core.resume_analyzer import ResumeAnalyzer
        assert ResumeAnalyzer is not None

    def test_import_matcher(self):
        from core.matcher import ExperienceMatcher
        assert ExperienceMatcher is not None

    def test_import_scorer(self):
        from core.scorer import FitScorer
        assert FitScorer is not None

    def test_import_rewriter(self):
        from core.rewriter import BulletRewriter
        assert BulletRewriter is not None


class TestUtilImports:
    """Test that utility modules import correctly."""

    def test_import_web_fetcher(self):
        from utils.web_fetcher import fetch_job_posting
        assert fetch_job_posting is not None

    def test_import_text_utils(self):
        from utils.text_utils import slugify, extract_metrics
        assert slugify is not None
        assert extract_metrics is not None


class TestTextUtils:
    """Test text utility functions."""

    def test_slugify(self):
        from utils.text_utils import slugify
        assert slugify("Acme Corp") == "acme-corp"
        assert slugify("Google Inc.") == "google-inc"
        assert slugify("Test  Multiple   Spaces") == "test-multiple-spaces"

    def test_slugify_special_chars(self):
        from utils.text_utils import slugify
        result = slugify("Company & Co!")
        assert "&" not in result
        assert "!" not in result


class TestAPIEndpoints:
    """Test FastAPI endpoints."""

    @pytest.fixture
    def client(self):
        from api import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "api_key_configured" in data

    def test_tailor_endpoint_validation(self, client):
        # Test with missing fields
        response = client.post("/api/tailor", json={})
        assert response.status_code == 422  # Validation error

    def test_tailor_endpoint_accepts_valid_request(self, client):
        response = client.post("/api/tailor", json={
            "resume_text": "# John Doe\n\n## Experience\n- Did stuff",
            "job_description": "Looking for a software engineer",
        })
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "status" in data

    def test_job_status_not_found(self, client):
        response = client.get("/api/jobs/nonexistent-job-id")
        assert response.status_code == 404

    def test_download_not_found(self, client):
        response = client.get("/api/download/nonexistent-file.docx")
        assert response.status_code == 404


class TestDataModels:
    """Test data model creation and serialization."""

    def test_contact_info_to_dict(self):
        from core import ContactInfo
        contact = ContactInfo(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
        )
        d = contact.to_dict()
        assert d["name"] == "John Doe"
        assert d["email"] == "john@example.com"

    def test_bullet_to_dict(self):
        from core import Bullet
        bullet = Bullet(
            text="Increased revenue by 50%",
            keywords=["revenue", "growth"],
            metrics=["50%"],
        )
        d = bullet.to_dict()
        assert d["text"] == "Increased revenue by 50%"
        assert "revenue" in d["keywords"]

    def test_role_to_dict(self):
        from core import Role, Bullet
        role = Role(
            title="Software Engineer",
            company="Acme Corp",
            start_date="2020-01",
            end_date="2023-01",
            location="San Francisco",
            bullets=[Bullet(text="Built stuff")],
        )
        d = role.to_dict()
        assert d["title"] == "Software Engineer"
        assert d["company"] == "Acme Corp"
        assert len(d["bullets"]) == 1
