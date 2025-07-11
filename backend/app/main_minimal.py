from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Email Responder", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Sample CSV download endpoint
@app.get("/api/sample-csv")
async def get_sample_csv():
    return {
        "filename": "prospects_sample.csv",
        "content": "email,first_name,last_name,company,phone,linkedin_url,company_domain,industry,company_linkedin_url,job_title,location,company_size,annual_revenue,lead_source\njohn.doe@example.com,John,Doe,Example Corp,+1-555-0123,https://linkedin.com/in/john-doe,example.com,Technology,https://linkedin.com/company/example-corp,CEO,San Francisco CA,100-500,$10M-$50M,Website\njane.smith@test.com,Jane,Smith,Test Inc,+1-555-0456,https://linkedin.com/in/jane-smith,test.com,Software,https://linkedin.com/company/test-inc,CTO,New York NY,50-100,$5M-$10M,LinkedIn\nmark.wilson@demo.org,Mark,Wilson,Demo Solutions,+1-555-0789,https://linkedin.com/in/mark-wilson,demo.org,Consulting,https://linkedin.com/company/demo-solutions,VP Sales,Austin TX,200-500,$25M-$50M,Referral"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)