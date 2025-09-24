#!/bin/bash

# Quick Demo Setup Script
# Prepares sample data and launches demo for presentation

set -e  # Exit on any error

echo "======================================"
echo "Clinical Research Pipeline Quick Demo"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check environment
print_status "Checking environment setup..."

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    print_error "run.py not found. Make sure you're in the assignment3/azure_xia directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. You may need to set up API credentials."
    echo "Create .env with:"
    echo "AMPLIFY_API_KEY=your_key"
    echo "AMPLIFY_API_URL=your_endpoint"
fi

# Check Python environment
if ! command -v python &> /dev/null; then
    print_error "Python not found. Please install Python."
    exit 1
fi

print_success "Environment check completed"

# Step 2: Install demo requirements
print_status "Installing demo requirements..."

if [ ! -f "requirements_demo.txt" ]; then
    print_warning "requirements_demo.txt not found, creating basic requirements..."
    cat > requirements_demo.txt << EOF
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
EOF
fi

pip install -r requirements_demo.txt > /dev/null 2>&1 || {
    print_warning "Failed to install some requirements. Demo may still work with existing packages."
}

print_success "Demo requirements installed"

# Step 3: Quick data preparation
print_status "Preparing demo data..."

# Check if we have existing data
if [ -f "outputs/step3_extracted.csv" ]; then
    print_success "Found existing clinical data for demo"
    
    # Show quick stats
    if command -v python &> /dev/null; then
        python3 -c "
import pandas as pd
try:
    df = pd.read_csv('outputs/step3_extracted.csv')
    print(f'   - {len(df)} clinical records available')
    print(f'   - Columns: {list(df.columns)[:5]}...')
except:
    print('   - Data file exists but may need regeneration')
"
    fi
else
    print_warning "No existing clinical data found"
    
    echo ""
    echo "Would you like to generate sample data for the demo? (y/n)"
    echo "This will run a quick core pipeline with minimal data:"
    echo "  - Keywords: depression OR anxiety"
    echo "  - Years: 2023-2024"
    echo "  - Sample: 20 papers per year"
    echo ""
    read -p "Generate sample data? [y/N]: " generate_data
    
    if [[ $generate_data =~ ^[Yy]$ ]]; then
        print_status "Generating sample clinical data..."
        print_warning "This may take 2-5 minutes depending on API response time..."
        
        # Run core pipeline with minimal settings
        if python3 run.py core --keywords "depression OR anxiety" --start-year 2023 --end-year 2024 --sample-per-year 20; then
            print_success "Sample data generated successfully!"
        else
            print_error "Failed to generate sample data. Demo will show with placeholder data."
        fi
    else
        print_status "Skipping data generation. Demo will show interface without live data."
    fi
fi

# Step 4: Launch demo
print_status "Preparing to launch demo..."

echo ""
echo "======================================"
echo "Demo Launch Options"
echo "======================================"
echo "1) Visualization Dashboard - Charts, insights, command builder"
echo "2) Interactive Runner - Live pipeline execution" 
echo "3) Unified Demo - Both modes in one interface (RECOMMENDED)"
echo "4) Exit"
echo ""

while true; do
    read -p "Choose demo mode [1-4]: " demo_choice
    case $demo_choice in
        1)
            print_status "Launching Visualization Dashboard..."
            print_success "Demo will open at http://localhost:8501"
            echo ""
            echo "Demo Features:"
            echo "  - Pipeline overview and agent status"
            echo "  - Interactive command builder"
            echo "  - Data flow visualizations"  
            echo "  - Impact factor analysis"
            echo "  - Agent integration showcase"
            echo ""
            streamlit run demo_visualization.py
            break
            ;;
        2)
            print_status "Launching Interactive Runner..."
            print_success "Demo will open at http://localhost:8501"
            echo ""
            echo "Demo Features:"
            echo "  - Live pipeline execution"
            echo "  - Custom parameter input"
            echo "  - Real-time output monitoring"
            echo "  - Results viewer and download"
            echo ""
            streamlit run demo_interactive_runner.py
            break
            ;;
        3)
            print_status "Launching Unified Demo Interface..."
            print_success "Demo will open at http://localhost:8501"
            echo ""
            echo "Demo Features:"
            echo "  - Switch between modes using sidebar"
            echo "  - Complete visualization dashboard"
            echo "  - Agent integration examples"
            echo "  - Professional interface for presentations"
            echo ""
            print_warning "Note: Use sidebar radio button to switch between visualization and interactive modes"
            streamlit run demo_visualization.py
            break
            ;;
        4)
            print_status "Exiting demo setup"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please select 1-4."
            ;;
    esac
done