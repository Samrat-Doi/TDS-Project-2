import os
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
import openai
from dotenv import load_dotenv
import zipfile
import io

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Set it in the .env file.")

openai.api_key = OPENAI_API_KEY

@app.post("/api/")
async def process_question(
    question: str = Form(...), file: UploadFile = File(None)
):
    extracted_text = ""
    
    if file:
        if not file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only .zip files are supported")
        
        # Read and extract zip file
        contents = await file.read()
        with zipfile.ZipFile(io.BytesIO(contents), "r") as zip_ref:
            for filename in zip_ref.namelist():
                with zip_ref.open(filename) as f:
                    extracted_text += f.read().decode("utf-8") + "\n"
        
        # Construct the prompt with extracted text
        prompt = f"Answer this question in one word or number only: {question}\n{extracted_text}"
    else:
        # Construct the prompt without extracted text
        prompt = f"Answer this question in one word or number only: {question}"
    
    print(prompt)
    
    # Get response from GPT-4o-mini
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    # Extract answer
    answer = response["choices"][0]["message"]["content"].strip()
    
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
