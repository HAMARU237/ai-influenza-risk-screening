import pandas as pd
from sklearn.model_selection import train_test_split

# =========================
# 1. Load dataset
# =========================

INPUT_FILE = "Deidentified_data_for_PLOS_2009_2014.csv"
OUTPUT_FILE = "influenza_clean.csv"

df = pd.read_csv(INPUT_FILE)

print("Original dataset shape:", df.shape)


# =========================
# 2. Select features
# =========================

features = [
    "Age",
    "Gender",
    "Sec3_Fever",
    "Sec3_Cough",
    "Sec3_Sore",
    "Sec3_Headache",
    "Sec3_Malaise",
    "Sec3_Runny",
    "Sec3_Generalized",
    "Sec3_Chill"
]

target = "Flu_final_posneg"

df = df[features + [target]].copy()


# =========================
# 3. Clean text values
# =========================

categorical_columns = [
    "Gender",
    "Sec3_Fever",
    "Sec3_Cough",
    "Sec3_Sore",
    "Sec3_Headache",
    "Sec3_Malaise",
    "Sec3_Runny",
    "Sec3_Generalized",
    "Sec3_Chill"
]

for column in categorical_columns:
    df[column] = df[column].astype(str).str.strip()


# =========================
# 4. Convert Yes / No
# =========================

for column in categorical_columns:
    if column != "Gender":
        df[column] = df[column].map({
            "Yes": 1,
            "No": 0
        })


# =========================
# 5. Convert Gender
# =========================

df["Gender"] = df["Gender"].map({
    "Male": 1,
    "Female": 0
})


# =========================
# 6. Remove invalid rows
# =========================

df = df.dropna()


# =========================
# 7. Save cleaned dataset
# =========================

df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned dataset shape:", df.shape)

print("\nTarget distribution:")
print(df[target].value_counts())

print("\nCleaned dataset:")
print(df.head())

print("\nSaved as:", OUTPUT_FILE)