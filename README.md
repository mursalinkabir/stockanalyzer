# Python Stock Analysis Dashboard

This project is a Python-based stock analysis tool that provides fundamental and sentiment analysis for technology stocks. It features a user-friendly dashboard built with Streamlit to visualize the data.

## Features

- **Fundamental Analysis**: Fetches and displays key metrics like P/E ratio, market capitalization, and dividend yield.
- **Sentiment Analysis**: Uses the Gemini API to perform deep research and analyze market sentiment for selected stocks.
- **Interactive Dashboard**: A clean and intuitive UI to display analysis results with interactive charts.
- **Customizable Stock List**: Analyze the top 30 tech stocks by default, or add your own tickers.

## Project Structure

```
.
├── main.py               # Main entry point for the Streamlit application
├── analysis.py           # Core logic for data fetching and analysis
├── ui.py                 # Streamlit user interface code
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Setup and Installation

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create a Virtual Environment (Recommended)

It's good practice to create a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install all the required Python libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up Your Gemini API Key

This project uses the Gemini API for sentiment analysis. You need to obtain an API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and set it as an environment variable.

**For macOS/Linux:**

```bash
export GEMINI_API_KEY='your_api_key_here'
```

**For Windows:**

```bash
set GEMINI_API_KEY='your_api_key_here'
```

> **Note**: You must replace `'your_api_key_here'` with your actual Gemini API key. For the changes to take permanent effect, you might need to add this line to your shell's startup file (e.g., `.bashrc`, `.zshrc`) or set it in your system's environment variable settings.

## How to Run the Application

Once you have completed the setup, you can run the Streamlit application with the following command:

```bash
streamlit run main.py
```

This will start the application and open it in your default web browser. From there, you can interact with the dashboard to analyze stocks.
