# GlassSlipper.ai

SteelHacks Hackathon Project 2025

## Team

- Raima Saha
- Emily Bartell
- Sahiti Kulkarni
- Lakshya Srinivasan

## About

GlassSlipper.ai lets users upload a photo of a celebrity they admire and receive personalized style recommendations inspired by that celebrity's look. The app detects the celebrity, analyzes their facial traits (gender, age, emotions, facial features, pose), and generates tailored suggestions for makeup, clothing, and jewelry/accessories.

## How It Works

1. Upload an image of a celebrity
2. Amazon Rekognition identifies the celebrity and detects facial traits (gender, age range, emotions, smile, eyeglasses, beard, etc.)
3. Claude AI generates style recommendations based on those traits, organized into:
   - **Drugstore Makeup** — budget-friendly product picks
   - **High-End Makeup** — premium product picks (matching the same categories as drugstore)
   - **Clothing Suggestions** — outfit pieces and styles that complement the look
   - **Jewelry & Accessories** — earrings, necklaces, hair accessories, etc.
   - **Application Tips** — how to apply and style the look

## Tech Stack

- **Frontend:** React (TypeScript) with Vite, styled with CSS, using react-markdown to render recommendations
- **Backend:** FastAPI (Python), serving a REST API at `POST /upload/demo_user`
- **Celebrity & Face Detection:** Amazon Rekognition (`recognize_celebrities` + `detect_faces`)
- **AI Recommendations:** Anthropic Claude API (claude-sonnet-4-20250514)

## Prerequisites

Before running the app, you need the following API keys and credentials:

- **AWS account** with access to [Amazon Rekognition](https://aws.amazon.com/rekognition/) in the `us-east-2` region. You'll need your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- **Anthropic API key** — sign up at [console.anthropic.com](https://console.anthropic.com/) to get your `ANTHROPIC_API_KEY`.

Create a `backend/.env` file with the following values:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Running Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## Future Plans

1. **User accounts & usage tracking:** Add authentication and a database (PostgreSQL) to track API usage per user and enforce rate limits.
2. **User-face analysis:** Allow users to upload a photo of their own face so recommendations are tailored to their features rather than a celebrity's.
3. **Deeper skin-tone analysis:** Improve prompting to factor in undertone and hue for more precise makeup and jewelry suggestions.
