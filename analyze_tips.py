import pandas as pd

def compare_avg_tip_by_smoker(filepath):
    """
    Compares the average tip amount for smokers versus non-smokers.

    Args:
        filepath (str): The path to the tips.csv file.

    Returns:
        pd.Series: A Series with the average tip for each smoker category.
                   Returns None if the file is not found.
    """
    try:
        # Load the CSV file into a Pandas DataFrame
        df = pd.read_csv(filepath)

        # Calculate the average tip, grouped by the 'smoker' column
        average_tips = df.groupby('smoker')['tip'].mean()

        return average_tips

    except FileNotFoundError:
        print(f"Error: The file at {filepath} was not found.")
        return None

# Example usage:
# Assuming 'tips.csv' is in the same directory as the script.
file_path = 'tips.csv'
average_tips_comparison = compare_avg_tip_by_smoker(file_path)

if average_tips_comparison is not None:
    print("Average tip amount comparison:")
    print(average_tips_comparison)

Average tip amount comparison:
smoker
No     2.991854
Yes    3.008710
Name: tip, dtype: float64
