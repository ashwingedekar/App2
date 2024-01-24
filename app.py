# app.py

from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        sensor_id = request.form['sensorId']
        start_date = request.form['startDate']
        end_date = request.form['endDate']
        avg = request.form['avg']
        username = request.form['username']
        passhash = request.form['passhash']
        speed_data_type = request.form.get('speedDataType', 'max')

        start_datetime = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

        start_date_str = start_datetime.strftime('%Y-%m-%d-%H-%M-%S')
        end_date_str = end_datetime.strftime('%Y-%m-%d-%H-%M-%S')

        api_endpoint = f'https://tp-prtg-101-100.comtelindia.com:10443/api/historicdata.csv?id={sensor_id}&avg={avg}&sdate={start_date_str}&edate={end_date_str}&username={username}&passhash={passhash}'

        response = requests.get(api_endpoint)

        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))

            if speed_data_type == 'min':
                speed_row = df.loc[df["Traffic Total (Speed)(RAW)"].idxmin()]
                speed_data_key = "min_speed_data"
            else:
                speed_row = df.loc[df["Traffic Total (Speed)(RAW)"].idxmax()]
                speed_data_key = "max_speed_data"

            current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_location = f"C:/prtg/output_{speed_data_type}_speed_{current_datetime}.csv"

            # Create a smaller DataFrame with only the relevant information
            output_df = pd.DataFrame({
                "Date Time": speed_row['Date Time'],
                "Traffic Total (Speed)": speed_row['Traffic Total (Speed)'],
                "Traffic Total (Speed)(RAW)": speed_row['Traffic Total (Speed)(RAW)'],
                "output_location": output_location
            }, index=[0])

            # Save the smaller DataFrame to a CSV file
            output_df.to_csv(output_location, index=False)

            # Prepare the result as a dictionary
            result_dict = {
                "success": True,
                "message": "Data fetched successfully.",
                speed_data_key: {
                    "Date Time": speed_row['Date Time'],
                    "Traffic Total (Speed)": speed_row['Traffic Total (Speed)'],
                    "Traffic Total (Speed)(RAW)": speed_row['Traffic Total (Speed)(RAW)'],
                    "output_location": output_location
                }
            }

            # Return the result as JSON
            return jsonify(result_dict)

        else:
            return jsonify({"success": False, "message": f"Error: {response.status_code} - {response.text}"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error processing CSV data: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
