# Smart Carbon Dashboard

An interactive webbased platform for exploring, comparing and predicting CO2 and greenhouse gas emissions data. Built using Python and Streamlit.

## Features
- Explore historical emissions data by country and emission type
- Compare emissions across countries, continents and economic blocs
- View short term CO2 emissions predictions with reliability indicators
- Explore Climate Success Stories for Norway, Germany and Denmark

## How to Run

1. Clone the repository:
git clone https://github.com/Anas9563/smart-carbon-dashboard.git

2. Install dependencies:
pip install -r requirements.txt

3. Navigate to the app folder:
cd app

4. Run the dashboard:
streamlit run Dashboard.py

5. The dashboard will open automatically in your browser.

## Data Source
- Our World in Data CO2 and Greenhouse Gas Emissions dataset
- Available at: https://github.com/owid/co2-data

## Project Structure
- app/ — Streamlit dashboard pages and case studies
- data/ — Cleaned dataset and raw OWID dataset
- notebooks/ — Jupyter notebooks for EDA, comparative analysis and prediction model

## Technologies
- Python
- Streamlit
- Plotly
- pandas
- scikit-learn
