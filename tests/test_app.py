import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import app  # Import app after modifying the path
import tempfile
import pytest



@pytest.fixture
def client():
    """Setup the test client and temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        app.config['UPLOAD_FOLDER'] = temp_dir
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client


def test_index_page(client):
    """Test the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Incident Analysis Dashboard" in response.data



def test_visualization_clustering(client):
    """Test accessing clustering visualization without data."""
    response = client.get('/visualization/clustering')
    assert response.status_code == 200
    assert b"No processed data found" in response.data


def test_ml_clustering(client):
    """Test accessing ML clustering visualization without data."""
    response = client.get('/visualization/ml_clustering')
    assert response.status_code == 200
    assert b"No processed data found" in response.data


def test_pie_chart(client):
    """Test accessing pie chart visualization without data."""
    response = client.get('/visualization/pie_chart')
    assert response.status_code == 200
    assert b"No processed data found" in response.data


def test_bar_graph(client):
    """Test accessing bar graph visualization without data."""
    response = client.get('/visualization/bar_graph')
    assert response.status_code == 200
    assert b"No processed data found" in response.data


def test_top_locations(client):
    """Test accessing top locations visualization without data."""
    response = client.get('/visualization/incidents_by_location')
    assert response.status_code == 200
    assert b"No processed data found" in response.data


def test_incidents_over_time(client):
    """Test accessing incidents over time visualization without data."""
    response = client.get('/visualization/incidents_over_time')
    assert response.status_code == 200
    assert b"No processed data found" in response.data
