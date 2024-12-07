# CIS6930FA24 -- Project 3: End Pipeline

**Name:** Prajay Yalamanchili

## Project Description
This project focuses on creating an end-to-end data visualization pipeline for processing and analyzing incident data. The application allows users to upload a PDF or provide a URL containing Norman Police Department incident data, extract the data, and visualize it using various graphs. The web application is built using Flask, with front-end templates styled for ease of use. Users can explore insights such as clustering of incidents by time and day, most common locations, and more.

## How to Install

**For Windows:**

1. If Python is not already installed on your system, download and install Python version 3.12 from [here](https://www.python.org/downloads/).
2. Set your path in the environment variables. To learn how to set the path in environment variables, read this [article](https://www.liquidweb.com/help-docs/adding-python-path-to-windows-10-or-11-path-environment-variable/).
3. Download or clone this repository using:
    ```bash
    git clone <repository-url>
    ```
4. Navigate to the project directory on your local machine.
5. Run the following commands:
    ```bash
    pip install pipenv
    ```
    ```bash
    pipenv install
    ```

## How to Run

1. To execute the `app.py` file, use:
    ```bash
    pipenv run python src/app.py
    ```
2. To run tests, use:
    ```bash
    pipenv run python -m pytest -v
    ```
    or
    ```bash
    pipenv run pytest
    ```

## Demo Program

[![Watch the video](https://img.youtube.com/vi/gdquTTwzoUQ/maxresdefault.jpg)](https://youtu.be/gdquTTwzoUQ)

### [Watch Demo Video](https://youtu.be/gdquTTwzoUQ)

[![Watch the video](https://img.youtube.com/vi/dl01pVJzB64/maxresdefault.jpg)](https://youtu.be/dl01pVJzB64)

### [Watch ML Clustering Visualization](https://youtu.be/dl01pVJzB64) (Not there in First Video)

## Folder Structure
```
|   COLLABORATORS.md
|   Pipfile
|   Pipfile.lock
|   README.md
|   setup.cfg
|   setup.py
|
+---resources
|       2024-10-11_daily_arrest_summary.pdf
|       incidents.csv
|       
|
+---src
|       app.py
|       main.py
|
+---static
|       error_style.css
|       home_style.css
|       style.css
|       success_page.css
|       visualization_style.css
|
\---templates
        error.html
        index.html
        upload_success.html
        visualization.html
        visualization_menu.html
```


### File Descriptions:

- **COLLABORATORS.md:** Contains information about collaborators and a list of resources used for the assignment.
- **src/app.py:** Contains the main logic for handling requests, processing data, and rendering visualizations.
- **src/main.py:** Contains utility functions for fetching and processing data from PDF/URL.
- **resources:** Folder containing example data files and processed CSV data.
- **templates:** HTML templates for rendering the web pages.
- **static:** Contains CSS files for styling the web pages.
- **Pipfile:** Manages the Python virtual environment and lists all dependencies.
- **Pipfile.lock:** Specifies the versions of dependencies to ensure consistent environments.
- **README.md:** This file, which documents the project.
- **LICENSE:** Contains licensing information, including copyright, publishing, and usage rights.

## User Interface

- **Home Page:** Users can upload a file or provide a URL to process incident data.
- **Visualization Dashboard:** After processing the data, users can select from multiple visualizations.
- **Error Page:** Displays appropriate error messages if invalid input is provided.
- **Success Page:** Informs users when their data has been processed successfully.

## Project Flow

1. **Input:**
   - User uploads a PDF file or provides a URL to fetch data.
2. **Processing:**
   - Data is extracted, transformed, and saved in a CSV format.
3. **Output:**
   - The user can visualize data using various graphs and insights.

## Visualization Graphs

1. **Incident Clustering by Day and Time (or Periods):** A heatmap providing insights into how incidents are distributed across different days of the week and times of the day for multiple files. For single-day data, a bar chart shows incidents clustered by time periods (Morning, Afternoon, Evening, Night). The heatmap or bar chart is particularly useful for identifying temporal patterns in incident occurrences and planning resource allocation accordingly.
2. **Bar Graph of Incidents by Nature:**  This bar graph visualizes the frequency of incidents categorized by their nature (e.g., theft, assault, public intoxication), where each bar represents a specific type of incident, and the height of the bar indicates its frequency. This graph helps in understanding which types of incidents are most common, aiding stakeholders such as law enforcement or community planners in focusing their efforts on the most prevalent issues.
3. **Incidents Over Time (Daily/Hourly Trends):**  A line chart that shows the trend of incidents recorded over a period of days for multiple files, with the x-axis representing the dates and the y-axis showing the number of incidents for each date. For single-day data, the chart dynamically adapts to show incidents over time on an hourly basis, providing insights into peak hours. This visualization highlights trends such as spikes or drops in incident counts during specific periods (e.g., holidays, weekends), providing valuable insights for trend analysis and resource planning to mitigate future surges.
4. **Pie Chart of Incidents by Day or Nature:** For multiple files, this pie chart breaks down the proportion of incidents by the day of the week, with each slice representing the percentage of incidents occurring on a specific day and labels showing percentages for clarity. For single-day data, the pie chart displays the proportion of incidents by their nature, focusing on the top 10 most frequent incident types, with remaining categories grouped under "Others" for clarity. This visualization provides a concise and clear representation of incident distribution patterns, enabling better scheduling, resource allocation, and targeted interventions based on incident frequency and type.
5. **Top Locations by Incidents:** A horizontal bar chart that highlights the top 10 locations with the highest number of reported incidents. Each bar corresponds to a specific location, with the bar length indicating the frequency of incidents. This graph identifies key hotspots where incidents occur most frequently, such as busy streets, neighborhoods, or public spaces, allowing for targeted interventions, enhanced surveillance, or increased patrolling in these areas to address the issues effectively.

## `app.py`

**Functions in `app.py`:**

### `index()`
- Displays the home page where users can upload a file or provide a URL, serving as the entry point for users to interact with the application, with a clean and user-friendly interface guiding them through the data upload process.

### `upload_pdf()`
- HHandles file uploads from the user, processes the uploaded data by extracting incidents from the PDF, saves it in a structured CSV format, and prepares it for visualization, ensuring that the file is validated and processed efficiently.

### `process_url()`
- Fetches and processes data directly from a user-provided URL by downloading the specified PDF file, extracting the relevant incident data, saving it in CSV format, and ensuring the data is ready for visualization while handling any errors gracefully.

### Visualization Routes:
- `/visualization/clustering`: Displays clustering of incidents by day and time.
- `/visualization/bar_graph`: Displays a bar graph of incidents by nature.
- `/visualization/incidents_over_time`: Shows a line graph of incidents over time.
- `/visualization/pie_chart`: Displays a pie chart of incidents by the day of the week.
- `/visualization/incidents_by_location`: Shows a bar graph of top 10 locations.

## `main.py`

**Functions in `main.py`:**

### `fetch_incidents(url)`
This function takes a URL as an argument, calls the Norman Police API to retrieve the PDF, saves it in the resources folder, and returns the name of the PDF file along with the status code.

### `extract_incidents(pdf_filepath)`
This function takes the name of the PDF file as an input argument, cleans the data, and extracts the incident information into a DataFrame. It returns the DataFrame.

### `parse_lines(row)`
This is a helper function for `extract_incidents(pdf_filepath)`. It uses regex to extract individual fields from string. It returns a list consisting of extracted information.

### `check_page(page)`
This is a helper function for `extract_incidents(pdf_filepath)`. It returns True if page is not empty else returns False.

## Assumptions and Limitations

- The input PDF or URL must follow a predefined format for proper data extraction.
- Limited to visualizing pre-defined insights; additional customization requires code changes.
- Current implementation assumes clean data; handling complex errors might need enhancements.

