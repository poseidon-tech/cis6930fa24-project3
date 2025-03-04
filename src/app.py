from flask import Flask, request, render_template, redirect, url_for, jsonify
from main import fetch_incidents, extract_incidents  
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import base64
matplotlib.use('Agg') 
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'resources')
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'templates')
app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=os.path.join(PROJECT_ROOT, 'static'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Saves the plot
def save_plot_as_image(plt):
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url


# Returns Index.html
@app.route('/')
def index():
    return render_template('index.html')

# Returns Upload.html
@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        files = request.files.getlist('files')  
        if not files or all(file.filename == '' for file in files):
            return redirect(url_for('error', message="No files selected. Please upload valid files."))
        all_incidents = []  
        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            incidents_df = extract_incidents(file_path)
            all_incidents.append(incidents_df)
        combined_df = pd.concat(all_incidents, ignore_index=True)
        incidents_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
        combined_df.to_csv(incidents_csv_path, index=False)

        return redirect(url_for('upload_success'))
    except Exception as e:
        return redirect(url_for('error', message=f"Error processing files: {str(e)}"))

# Process URL
@app.route('/process_url', methods=['POST'])
def process_url():
    try:
        file_urls = request.form.get('file_urls')
        file_urls = [url.strip() for url in file_urls.split(',') if url.strip()]
        if not file_urls or all(url.strip() == '' for url in file_urls):
            return redirect(url_for('error', message="No URLs provided. Please provide valid URLs."))
        print(file_urls)
        all_incidents = []  
        for file_url in file_urls:
            status, file_path = fetch_incidents(file_url)
            if status == 200:
                incidents_df = extract_incidents(file_path)
                all_incidents.append(incidents_df)
            else:
                return redirect(url_for('error', message=f"Failed to fetch the file from URL: {file_url}. Status: {status}"))
        combined_df = pd.concat(all_incidents, ignore_index=True)
        incidents_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
        combined_df.to_csv(incidents_csv_path, index=False)

        return redirect(url_for('upload_success'))
    except Exception as e:
        return redirect(url_for('error', message=f"Error processing URLs:"))


# Returns Success message
@app.route('/upload_success')
def upload_success():
    return render_template('upload_success.html')


# Returns Visualization Dashboard
@app.route('/visualization_menu')
def visualization_menu():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return redirect(url_for('error', message="No data uploaded. Please upload a file or provide a URL."))
    return render_template('visualization_menu.html')

# Returns Error message
@app.route('/error')
def error():
    message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', message=message)

# Visualization : Grouping of Records by Day and Time
@app.route('/visualization/clustering', methods=['GET'])
def clustering():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload or process a file first.'})
    data = pd.read_csv(data_path)
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    data['Time of Day'] = data['Date / Time'].dt.hour.apply(
        lambda x: 'Morning' if 6 <= x < 12 else
                  'Afternoon' if 12 <= x < 18 else
                  'Evening' if 18 <= x < 24 else
                  'Night'
    ) 
    unique_dates = data['Date / Time'].dt.date.nunique()
    if unique_dates > 1:
        data['Day of the Week'] = data['Date / Time'].dt.day_name()  
        clustering_data = data.groupby(['Day of the Week', 'Time of Day']).size().unstack(fill_value=0)
        plt.figure(figsize=(12, 8))
        sns.heatmap(clustering_data, annot=True, fmt="d", cmap="coolwarm")
        plt.title("Incident Clustering by Day and Time")
        plt.xlabel("Time of Day")
        plt.ylabel("Day of the Week")
    else:
        clustering_data = data['Time of Day'].value_counts().reindex(['Morning', 'Afternoon', 'Evening', 'Night'], fill_value=0)
        plt.figure(figsize=(12, 6))
        clustering_data.plot(kind='bar', color='skyblue')
        plt.title("Incident Clustering by Time of Day")
        plt.xlabel("Time of Day")
        plt.ylabel("Number of Incidents")
        plt.xticks(rotation=0)
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


# Visualization 3: Incidents Over Time (Daily/Hourly Trends):
@app.route('/visualization/incidents_over_time', methods=['GET'])
def incidents_over_time():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})
    data = pd.read_csv(data_path)
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    unique_dates = data['Date / Time'].dt.date.nunique()
    if unique_dates > 1:
        data['Date'] = data['Date / Time'].dt.date  
        daily_incidents = data.groupby('Date').size()
        plt.figure(figsize=(12, 6))
        daily_incidents.plot(kind='line', marker='o', color='blue')
        plt.title("Number of Incidents Over Time")
        plt.xlabel("Date")
        plt.ylabel("Number of Incidents")
        plt.xticks(rotation=45)
    else:
        data['Hour'] = data['Date / Time'].dt.hour
        hourly_incidents = data.groupby('Hour').size()
        plt.figure(figsize=(12, 6))
        hourly_incidents.plot(kind='line', marker='o', color='blue')
        plt.title("Number of Incidents Over Time (Hourly)")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Number of Incidents")
        plt.xticks(range(0, 24), rotation=45)
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)


# Visualization 4: Pie Chart of Incidents by Day or Nature
@app.route('/visualization/pie_chart', methods=['GET'])
def pie_chart():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})
    data = pd.read_csv(data_path)
    if 'Date / Time' not in data.columns:
        return jsonify({'error': "'Date / Time' column is missing in the data."})
    data['Date / Time'] = pd.to_datetime(data['Date / Time'])
    unique_dates = data['Date / Time'].dt.date.nunique()

    if unique_dates > 1:
        data['Day of the Week'] = data['Date / Time'].dt.day_name()
        day_counts = data['Day of the Week'].value_counts()
        plt.figure(figsize=(8, 8))
        day_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Pastel1')
        plt.title("Incident Distribution by Day of the Week")
        plt.ylabel("")  
    else:
        nature_counts = data['Nature'].value_counts()
        top_10 = nature_counts[:10]
        others_count = nature_counts[10:].sum()
        if others_count > 0:
            top_10["Others"] = others_count
        plt.figure(figsize=(8, 8))
        top_10.plot(kind='pie', autopct='%1.1f%%', startangle=140, colormap='Pastel2')
        plt.title("Incident Distribution by Nature")
        plt.ylabel("")  
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)


# Visualization 5: Top Locations by Incidents
@app.route('/visualization/incidents_by_location', methods=['GET'])
def incidents_by_location():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload a PDF or provide a URL.'})
    data = pd.read_csv(data_path)
    if 'Location' not in data.columns:
        return jsonify({'error': "'Location' column is missing in the data."})
    location_counts = data['Location'].value_counts().head(10)  # Top 10 locations
    plt.figure(figsize=(12, 6))
    location_counts.sort_values().plot(kind='barh', color='green')
    plt.title("Top 10 Locations by Number of Incidents")
    plt.xlabel("Number of Incidents")
    plt.ylabel("Location")
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)


# Visualization 1: K-means clustering
@app.route('/visualization/ml_clustering', methods=['GET'])
def ml_clustering_scatter_improved_v2():
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], 'incidents.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No processed data found! Please upload or process a file first.'})
    data = pd.read_csv(data_path)
    if 'Nature' not in data.columns:
        return jsonify({'error': "'Nature' column is missing in the data."})
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(data['Nature'])
    n_clusters = 5  # Number of clusters
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    data['Cluster'] = kmeans.fit_predict(X)
    cluster_labels = {}
    for cluster in range(n_clusters):
        cluster_labels[cluster] = ", ".join(
            data[data['Cluster'] == cluster]['Nature'].value_counts().index[:4]
        )
    plt.figure(figsize=(14, 8))  # Increase graph area
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for cluster in range(n_clusters):
        cluster_data = data[data['Cluster'] == cluster]
        plt.scatter(
            np.random.rand(len(cluster_data)),  # Randomized x-axis for scatter effect
            range(len(cluster_data)),
            c=colors[cluster],
            label=f"Cluster {cluster}: {cluster_labels[cluster]}",
            alpha=0.6,
            edgecolors='w'
        ) 
    plt.title("Incident Clustering by Nature (K-Means) K =5 ", fontsize=16)
    plt.xlabel("X-Axis (Clusters)", fontsize=12)
    plt.ylabel("Incident Instances", fontsize=12)
    plt.legend(
        title="Clusters",
        bbox_to_anchor=(1.15, 1),  # Further outside
        loc='upper left',
        fontsize='small',  # Reduce font size
        title_fontsize='medium',
        frameon=False
    )
    plt.tight_layout()
    plot_url = save_plot_as_image(plt)
    return render_template('visualization.html', plot_url=plot_url)




if __name__ == '__main__':
    app.run(debug=True)