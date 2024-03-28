# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import db

# Read data from the database into a DataFrame
# Replace 'your_database_connection_parameters' with actual connection parameters
conn = db.connect_to_database()
query = 'SELECT * FROM home_info;'
df = pd.read_sql(query, conn)

# Display the first few rows of the DataFrame
print("First few rows of the DataFrame:")
print(df.head())

# Check for missing values in each column
print("\nMissing values in each column:")
print(df.isnull().sum())

# Check unique values and their counts for each attribute
attributes = ['source_system', 'status', 'home_type', 'bedrooms', 'bathrooms', 'year_built', 'new_construction', 'has_pool']
for attribute in attributes:
    print(f"\nUnique values and their counts for '{attribute}':")
    print(df[attribute].value_counts())

# Plot distribution of numeric attributes
numeric_attributes = ['finished_sqft', 'lot_size_sqft', 'bedrooms', 'bathrooms', 'year_built']
for attribute in numeric_attributes:
    plt.figure(figsize=(8, 6))
    sns.histplot(df[attribute], bins=20, kde=True, color='skyblue')
    plt.title(f'Distribution of {attribute}')
    plt.xlabel(attribute)
    plt.ylabel('Frequency')
    plt.show()

# Explore correlations between numeric attributes
numeric_df = df[numeric_attributes]
correlation_matrix = numeric_df.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# Identify outliers or anomalies in the data
# Example: Plot boxplots for numeric attributes
plt.figure(figsize=(12, 6))
sns.boxplot(data=df[['finished_sqft', 'lot_size_sqft']])
plt.title('Boxplots of Numeric Attributes')
plt.show()

# Perform summary statistics for numeric attributes
summary_statistics = df[numeric_attributes].describe()
print(summary_statistics)
