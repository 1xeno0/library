#!/bin/bash

echo "🎯 Patchwork Clips Analyzer Demo Setup"
echo "======================================"

# Check if we're in the right directory
if [ ! -d "video_analysis_system" ]; then
    echo "❌ Please run this script from the Library For Patchwork directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔧 Checking dependencies..."

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ All dependencies found"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd video_analysis_system

# Install Python dependencies if needed
if [ ! -f "requirements_installed.flag" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    touch requirements_installed.flag
    echo "✅ Python dependencies installed"
else
    echo "✅ Python dependencies already installed"
fi

# Go back to root
cd ..

# Setup frontend if it doesn't exist
if [ ! -d "patchwork-demo" ]; then
    echo ""
    echo "🔧 Setting up frontend..."
    
    # Create React app
    echo "📦 Creating React app with TypeScript..."
    npx create-react-app patchwork-demo --template typescript
    
    cd patchwork-demo
    
    # Install additional dependencies
    echo "📦 Installing additional dependencies..."
    npm install axios @tanstack/react-query
    npm install @headlessui/react @heroicons/react
    npm install tailwindcss @tailwindcss/forms @tailwindcss/typography
    npm install react-router-dom
    npm install react-hot-toast
    npm install framer-motion
    
    # Setup Tailwind CSS
    echo "🎨 Setting up Tailwind CSS..."
    npx tailwindcss init -p
    
    echo "✅ Frontend setup complete"
    cd ..
else
    echo "✅ Frontend already exists"
fi

# Create demo start script
echo ""
echo "📝 Creating demo start scripts..."

# Backend start script
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Patchwork Analysis Backend..."
cd video_analysis_system
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 app.py
EOF

# Frontend start script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Patchwork Demo Frontend..."
cd patchwork-demo
npm start
EOF

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

# Create a comprehensive demo script
cat > demo-instructions.md << 'EOF'
# 🎯 Patchwork Clips Analyzer Demo

## 🚀 Quick Start

### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

### Option 2: Test Backend Only
```bash
cd video_analysis_system
python3 app.py

# Test in another terminal:
curl http://localhost:5050/stats
curl http://localhost:5050/patchwork/streams
```

## 📋 Demo Flow

### 1. Backend API Testing
```bash
# Get Patchwork stats
curl http://localhost:5050/stats

# Get available streams
curl http://localhost:5050/patchwork/streams

# Get clips from coscu
curl "http://localhost:5050/patchwork/clips?username=coscu&limit=5"

# Analyze a clip
curl -X POST http://localhost:5050/analyse \
  -H "Content-Type: application/json" \
  -d '{"video_link": "REAL_CLIP_URL", "streamer_name": "coscu"}'
```

### 2. Frontend Demo (Once React app is ready)
1. **Dashboard** - Shows live stats from Patchwork API
2. **Clip Browser** - Browse real clips with analyze buttons
3. **Analysis Demo** - Click analyze and see real-time progress
4. **Search** - Search analyzed clips by content
5. **Batch Analysis** - Select multiple clips for batch processing

## 🔧 Development Notes

### Backend Endpoints Available:
- `GET /stats` - System statistics
- `GET /patchwork/streams` - Available streamers
- `GET /patchwork/clips` - Available clips
- `POST /analyse` - Analyze single clip
- `POST /analyse/batch` - Batch analysis
- `GET /analyse/progress/<job_id>` - Progress tracking
- `POST /find_clips` - Search analyzed clips

### Frontend Components to Build:
- Dashboard with stats cards
- Clip browser with grid layout
- Analysis modal with progress
- Search interface
- Batch analysis interface

## 🎮 Demo Data

Real streamers available:
- coscu (kick) - Gaming content
- lacy (kick) - Various content  
- n3on (kick) - Gaming content
- PBDPodcast (youtube) - Podcast content

## 🚨 Troubleshooting

1. **Backend won't start**: Check Python dependencies
2. **No clips found**: Patchwork API might be down
3. **Analysis fails**: Check OpenAI API key
4. **Frontend errors**: Run `npm install` in patchwork-demo/

EOF

echo ""
echo "✅ Demo setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Start backend: ./start-backend.sh"
echo "2. Test API: curl http://localhost:5050/stats"
echo "3. Start frontend: ./start-frontend.sh (when ready)"
echo "4. Read demo-instructions.md for detailed guide"
echo ""
echo "🎯 Demo will be available at:"
echo "   Backend API: http://localhost:5050"
echo "   Frontend: http://localhost:3000 (when started)"
echo ""
echo "🔥 Ready to demo the Patchwork Clips Analyzer!" 