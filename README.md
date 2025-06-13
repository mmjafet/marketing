# Marketing Dashboard

This project is a web application built using Flask that provides a graphical interface for visualizing marketing data. The application allows users to interact with various charts generated from sales data, facilitating data analysis and insights.

## Project Structure

```
marketing-dashboard
├── app.py                     # Main entry point of the Flask application
├── static                     # Static files (CSS, JavaScript)
│   ├── css
│   │   └── tailwind.css       # Tailwind CSS styles for the application
│   └── js
│       └── chart_handlers.js   # JavaScript functions for handling chart rendering
├── templates                  # HTML templates for rendering the web pages
│   ├── base.html              # Base template with common structure
│   ├── index.html             # Main page with buttons for each chart
│   └── components
│       └── chart_container.html # Reusable component for displaying charts
├── utils                      # Utility modules for data processing and visualization
│   ├── data_processor.py      # Functions for processing sales data
│   └── visualization.py       # Functions for generating charts
├── data                       # Directory containing data files
│   └── sales_data_sample.csv  # Sample sales data for analysis
├── requirements.txt           # List of dependencies for the project
└── README.md                  # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd marketing-dashboard
   ```

2. **Install dependencies**:
   It is recommended to create a virtual environment before installing the dependencies.
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000` to view the marketing dashboard.

## Usage

- The main page features buttons for each chart available in the application.
- Clicking a button will render the corresponding chart using data from the sales dataset.
- The application utilizes Tailwind CSS for styling, ensuring a responsive and modern user interface.

## Features

- Interactive charts for data visualization.
- Responsive design using Tailwind CSS.
- Modular structure with reusable components for maintainability.

## Acknowledgments

This project utilizes various libraries including Flask, Pandas, Matplotlib, Seaborn, and Plotly for data processing and visualization.# representacion_graficas_marketing
# marketing
# marketing
