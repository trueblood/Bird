import joblib
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import pickle
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import plotly.graph_objects as go

class CollisionForecastARIMA:
    def __init__(self, data=None, columns=None):
        """
        Initializes the CollisionForecastARIMA object with collision data and column names.
        
        Parameters:
        - data: DataFrame containing collision data.
        - columns: A list of column names to be used in the ARIMA model.
        """
        self.data = data
        self.columns = columns
        self.model_fit = None

    def prepare_data(self):
        """
        Prepares the time series data by aggregating collision counts per day based on specified columns.
        """
        # Assumes the first column in self.columns is the time column for aggregation
        time_column = self.columns[0]
        self.data[time_column] = pd.to_datetime(self.data[time_column])
        self.collision_counts = self.data.groupby(self.data[time_column].dt.date).size()
        self.collision_counts.index = pd.to_datetime(self.collision_counts.index)
    
    def fit_model(self, order=(1,1,1)):
        """
        Fits an ARIMA model to the prepared time series data.
        
        Parameters:
        - order: A tuple (p, d, q) representing the ARIMA model parameters.
        """
        self.model = ARIMA(self.collision_counts, order=order)
        self.model_fit = self.model.fit()

    def forecast(self, steps=10):
        """
        Forecasts future collision counts.
        
        Parameters:
        - steps: The number of future time periods to forecast.
        
        Returns:
        - A forecast object containing the forecasted values.
        """
        if self.model_fit is None:
            print("Model is not fitted. Call fit_model() first.")
            return None
        forecast = self.model_fit.forecast(steps=steps)
        return forecast

    def load_model(self, filename):
        print("in load_model")
        try:
            print("in try load_model")
            return joblib.load(filename)
        except Exception as e:
            print("Model not found. Exception:", str(e))
            return None
    
    def save_model(self, file_name):
        joblib.dump(self, file_name)

# Usage example
if __name__ == "__main__":
    # Load your data here
    data_path = '../datasets/turbines/detailed_wind_turbine_collisions_bk.csv'
    
    data = pd.read_csv(data_path)
    
    # Simulating the loading of data with a 'BirdSpecies' column for the example
    data = pd.DataFrame({
         'Timestamp': pd.date_range(start='2023-01-01', periods=120, freq='D'),
         'Collisions': [i + (i % 10) for i in range(120)],
         'BirdSpecies': ['Hawk' if i % 2 == 0 else 'Sparrow' for i in range(120)]
     })
    
    # Specify the column names (time column first)
    columns = ['Timestamp']
    
    # Initialize the forecasting object with your data and column names
    forecast_arima = CollisionForecastARIMA(data, columns)
    
    # Prepare the data
    forecast_arima.prepare_data()
    
    # Fit the ARIMA model
    forecast_arima.fit_model(order=(1, 1, 1))
    
    model_filename = 'arima_model_forecasting.joblib'
    forecast_arima.save_model(model_filename)

    # Save the model to a file

    model = forecast_arima.load_model(model_filename)
    
    # Forecast future collision counts
    future_collisions = model.forecast(steps=10)
    print(future_collisions)

# Plotting historical data and forecasted values
    fig = go.Figure()
    # Plot historical data for each bird species
    for species in data['BirdSpecies'].unique():
        species_data = data[data['BirdSpecies'] == species]
        # Group by date and count collisions
        species_counts = species_data.groupby(species_data['Timestamp'].dt.date).size()
        fig.add_trace(go.Scatter(x=species_counts.index, y=species_counts, mode='lines', name=f'{species} - Historical'))

    # Add the aggregated forecast data
    # Assuming future_collisions is a Series with datetime index and collision counts
    forecast_index = future_collisions.index
    fig.add_trace(go.Scatter(x=forecast_index, y=future_collisions, mode='lines+markers', name='Aggregated Forecast', line=dict(dash='dot')))

    # Update layout
    fig.update_layout(title='Collision Counts and Forecast by Bird Species',
                    xaxis_title='Date',
                    yaxis_title='Number of Collisions',
                    xaxis_rangeslider_visible=True)

    # Show the figure
    fig.show()