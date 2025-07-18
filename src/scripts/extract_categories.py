import csv

# Read the CSV file and extract distinct categories
distinct_categories = set()

with open('../data/UpdatedResumeDataSet.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # Skip header row
    
    for row in csv_reader:
        if row:  # Check if row is not empty
            distinct_categories.add(row[0])

# Convert to sorted list for consistent output
distinct_categories = sorted(list(distinct_categories))

# Print the distinct categories
print("Distinct categories:")
for category in distinct_categories:
    print(f"- {category}")

# Save to a text file
with open('../distinct_categories.txt', 'w') as f:
    f.write("Distinct categories:\n")
    for category in distinct_categories:
        f.write(f"- {category}\n")

print(f"\nTotal number of distinct categories: {len(distinct_categories)}")
print("Categories saved to 'distinct_categories.txt'")