# Deployment Guide for Turtle Soup Game Server

## Deployment Options

### Option 1: Render (Recommended - Free tier available)

1. **Create Account**: Sign up at [render.com](https://render.com)

2. **Connect GitHub**:
   - Push your code to GitHub
   - Connect your GitHub account to Render

3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Select your repository
   - Render will auto-detect Python and use `render.yaml`

4. **Configure Environment**:
   - No additional config needed (uses render.yaml)
   - Service will be available at `https://your-app.onrender.com`

### Option 2: Railway (Simple deployment)

1. **Create Account**: Sign up at [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login and deploy
   railway login
   railway up
   ```

3. **Or Deploy via Dashboard**:
   - Connect GitHub repository
   - Railway will auto-detect configuration from `railway.json`

### Option 3: Heroku (Professional, paid)

1. **Create Account**: Sign up at [heroku.com](https://heroku.com)

2. **Install Heroku CLI**:
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

3. **Deploy**:
   ```bash
   # Login to Heroku
   heroku login

   # Create app
   heroku create your-app-name

   # Deploy
   git push heroku main
   ```

### Option 4: Vercel (For serverless)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Create `vercel.json`**:
   ```json
   {
     "builds": [{
       "src": "app.py",
       "use": "@vercel/python"
     }],
     "routes": [{
       "src": "/(.*)",
       "dest": "app.py"
     }]
   }
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

## Environment Variables

Set these in your deployment platform's dashboard:

```bash
# Required for OpenAI functionality
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=http://api.0ha.top/v1  # or https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Optional
PORT=5002  # Most platforms set this automatically
```

## Post-Deployment Steps

1. **Test Health Endpoint**:
   ```bash
   curl https://your-app.herokuapp.com/health
   ```

2. **Test Game API**:
   ```bash
   curl -X POST https://your-app.herokuapp.com/api/game/start \
     -H "Content-Type: application/json" \
     -d '{"problem_id": "chem_001"}'
   ```

3. **Access Test Interface**:
   - Navigate to `https://your-app.herokuapp.com/test`

## Important Notes

- **File Storage**: Current implementation uses file system storage. For production, consider:
  - AWS S3 for file storage
  - Redis for session management
  - PostgreSQL for persistent data

- **Session Management**: Sessions are in-memory and will reset on deployment. Consider using Redis for production.

- **API Keys**: Never commit API keys to git. Always use environment variables.

- **CORS**: Currently allows all origins. Restrict in production:
  ```python
  CORS(app, origins=['https://your-frontend.com'])
  ```

## Monitoring

- **Render**: Built-in monitoring dashboard
- **Railway**: Metrics in dashboard
- **Heroku**: Use Heroku metrics or New Relic add-on
- **All platforms**: Consider adding Sentry for error tracking

## Troubleshooting

### Port Issues
Most platforms set PORT automatically. The app already reads from environment:
```python
port = int(os.environ.get('PORT', 5002))
```

### Module Import Errors
Ensure `requirements.txt` is complete and uses specific versions.

### Memory Issues
If using free tier with limited memory:
- Reduce ThreadPoolExecutor workers
- Implement proper session cleanup
- Consider serverless options

### Timeout Issues
Free tiers often have 30-second request timeouts. For long AI operations:
- Implement webhooks
- Use background jobs
- Consider upgrading to paid tier