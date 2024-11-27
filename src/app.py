from flask import Flask, request, render_template, redirect, url_for, jsonify
from main import fetch_incidents, extract_incidents  # Import functions from Assignment 0
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
matplotlib.use('Agg') 
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'resources')
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=os.path.join(PROJECT_ROOT, 'static'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Helper function to save and return a base64-encoded image for visualization
def save_plot_as_image(plt):
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return redirect(url_for('error', message="No file selected. Please upload a valid file."))

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Extract incidents and save as CSV
        incidents_df = extract_incidents(file_path)
        incidents_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
        incidents_df.to_csv(incidents_csv_path, index=False)

        return redirect(url_for('upload_success'))
    except Exception as e:
        return redirect(url_for('error', message=f"Error processing file: {str(e)}"))


@app.route('/process_url', methods=['POST'])
def process_url():
    try:
        file_url = request.form.get('file_url')
        if not file_url:
            return redirect(url_for('error', message="No URL provided. Please provide a valid URL."))

        status, file_path = fetch_incidents(file_url)
        if status == 200:
            incidents_df = extract_incidents(file_path)
            incidents_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
            incidents_df.to_csv(incidents_csv_path, index=False)
            return redirect(url_for('upload_success'))
        else:
            return redirect(url_for('error', message=f"Failed to fetch the file from the URL. Status: {status}"))
    except Exception as e:
        return redirect(url_for('error', message=f"Error processing URL: {str(e)}"))


@app.route('/upload_success')
def upload_success():
    return render_template('upload_success.html')


@app.route('/visualization_menu')
def visualization_menu():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return redirect(url_for('error', message="No data uploaded. Please upload a file or provide a URL."))
    return render_template('visualization_menu.html')


@app.route('/error')
def error():
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', message=message)

# Visualization 1: Clustering of Records by Day and Time
@app.route('/visualization/clustering', methods=['GET'])
def clustering():
    # Ensure incidents.csv exists
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload or process a file first.'})

    # Load the data
    data = pd.read_csv(data_path)

    # Ensure the 'Date / Time' column exists
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})

    # Parse the 'Date / Time' column
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    data['Day of the Week'] = data['Date / Time'].dt.day_name()  # Extract day of the week
    data['Time of Day'] = data['Date / Time'].dt.hour.apply(
        lambda x: 'Morning' if 6 <= x < 12 else
                  'Afternoon' if 12 <= x < 18 else
                  'Evening' if 18 <= x < 24 else
                  'Night'
    )  # Categorize time of day

    # Group and create clustering data
    clustering_data = data.groupby(['Day of the Week', 'Time of Day']).size().unstack(fill_value=0)

    # Plot the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(clustering_data, annot=True, fmt="d", cmap="coolwarm")
    plt.title("Incident Clustering by Day and Time")
    plt.xlabel("Time of Day")
    plt.ylabel("Day of the Week")

    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)



# Visualization 2: Bar Graph - Comparison of Incident Counts by Nature
@app.route('/visualization/bar_graph', methods=['GET'])
def bar_graph():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})

    data = pd.read_csv(data_path)
    nature_counts = data['Nature'].value_counts()

    plt.figure(figsize=(12, 8))
    sns.barplot(x=nature_counts.values, y=nature_counts.index)
    plt.xlabel("Number of Incidents")
    plt.ylabel("Nature")
    plt.title("Comparison of Incident Counts by Nature")

    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)


@app.route('/visualization/incidents_over_time', methods=['GET'])
def incidents_over_time():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})

    # Load the data
    data = pd.read_csv(data_path)

    # Ensure the 'Date / Time' column exists
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})

    # Parse 'Date / Time' and extract the date
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    data['Date'] = data['Date / Time'].dt.date  # Extract the date (without time)

    # Count incidents per day
    daily_incidents = data.groupby('Date').size()

    # Create the line chart
    plt.figure(figsize=(12, 6))
    daily_incidents.plot(kind='line', marker='o', color='blue')
    plt.title("Number of Incidents Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Incidents")
    plt.xticks(rotation=45)

    # Save and render the plot
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)

@app.route('/visualization/pie_chart', methods=['GET'])
def pie_chart():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})

    # Load the data
    data = pd.read_csv(data_path)

    # Ensure the 'Date / Time' column exists
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})

    # Parse the 'Date / Time' column to derive 'Day of the Week'
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    data['Day of the Week'] = data['Date / Time'].dt.day_name()  # Extract day of the week

    # Count incidents by day of the week
    day_counts = data['Day of the Week'].value_counts()

    # Create the pie chart
    plt.figure(figsize=(8, 8))
    day_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Pastel1')
    plt.title("Crime Distribution by Day of the Week")
    plt.ylabel("")  # Hide the y-label for better aesthetics

    # Save and render the plot
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)


@app.route('/visualization/incidents_by_location', methods=['GET'])
def incidents_by_location():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})

    # Load the data
    data = pd.read_csv(data_path)

    # Ensure the 'Location' column exists
    if 'Location' not in data.columns:
        return jsonify({'error': "'Location' column is missing in the data."})

    # Count incidents by location
    location_counts = data['Location'].value_counts().head(10)  # Top 10 locations

    # Create the horizontal bar chart
    plt.figure(figsize=(12, 6))
    location_counts.sort_values().plot(kind='barh', color='green')
    plt.title("Top 10 Locations by Number of Incidents")
    plt.xlabel("Number of Incidents")
    plt.ylabel("Location")

    # Save and render the plot
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)



if __name__ == '__main__':
    app.run(debug=True)
