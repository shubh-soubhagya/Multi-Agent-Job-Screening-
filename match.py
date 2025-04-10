import pandas as pd
import ollama
from tqdm import tqdm

# Load data
cv_df = pd.read_csv(r"cv_analysis_output.csv")
jd_df = pd.read_csv(r"jobs_summary_extracted.csv")

# Clean column names
cv_df.columns = cv_df.columns.str.strip()
jd_df.columns = jd_df.columns.str.strip()

# Output rows
output_rows = []

print("🔍 Matching CVs with Job Descriptions...\n")

# Loop through CV rows
for _, cv_row in tqdm(cv_df.iterrows(), total=len(cv_df)):
    job_role = cv_row['job_role'].strip()
    matching_jd = jd_df[jd_df['Job Title'].str.strip() == job_role]

    if matching_jd.empty:
        match_score = "N/A"
    else:
        jd_row = matching_jd.iloc[0]

        # Prepare the prompt comparing cv_extracted_info and extracted_info
        prompt = f"""
You are a resume-job match evaluator.

Compare the candidate's extracted CV info and the job description info and give a match score between 0-100 based only on content relevance and contextual alignment.

Respond with ONLY a number.

### Candidate Info:
{cv_row['cv_extracted_info']}

### Job Description Info:
{jd_row['extracted_info']}
"""

        try:
            response = ollama.chat(model="gemma2:2b", messages=[
                {"role": "system", "content": "You are a resume-job match evaluator. Respond with only a number from 0 to 100."},
                {"role": "user", "content": prompt}
            ])
            content = response['message']['content'].strip()
            match_score = int(''.join(filter(str.isdigit, content)))
        except Exception as e:
            print(f"❌ Error processing: {e}")
            match_score = "Error"

    # Append result
    output_rows.append({
        "applicant_name": cv_row["applicant_name"],
        "email": cv_row["email"],
        "phone_no": cv_row["phone_no"],
        "job_role": job_role,
        "match_score": match_score
    })

# Create DataFrame
results_df = pd.DataFrame(output_rows)

# Save output
results_df.to_csv("cv_match_scores.csv", index=False)
print("\n✅ Matching complete. Results saved to 'cv_match_scores.csv'")
