#!/bin/bash

# Clinical Research Pipeline Demo Launcher
echo "Clinical Research Pipeline Demo"
echo "==============================="

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing demo requirements..."
    pip install -r requirements_demo.txt
fi

echo ""
echo "Demo Mode Options:"
echo "1) Visualization Dashboard - Charts, insights, and command builder"
echo "2) Interactive Runner - Live pipeline execution with custom parameters"
echo "3) Unified Demo - Single interface with both modes"
echo ""
read -p "Enter choice (1, 2, or 3): " choice

case $choice in
    1)
        echo ""
        echo "Launching visualization dashboard..."
        echo "Opening at http://localhost:8501"
        echo ""
        echo "Features:"
        echo "  - Multi-agent architecture overview"
        echo "  - Interactive command builder"
        echo "  - Data flow visualizations"
        echo "  - Clinical insights analysis"
        echo ""
        streamlit run demo_visualization.py
        ;;
    2)
        echo ""
        echo "Launching interactive runner..."
        echo "Opening at http://localhost:8501"
        echo ""
        echo "Features:"
        echo "  - Live pipeline execution"
        echo "  - Custom parameter input"
        echo "  - Real-time output monitoring"
        echo "  - Results viewer"
        echo ""
        streamlit run demo_interactive_runner.py
        ;;
    3)
        echo ""
        echo "Launching unified demo interface..."
        echo "Opening at http://localhost:8501"
        echo ""
        echo "Note: Switch between modes using the sidebar radio button"
        echo ""
        streamlit run demo_visualization.py
        ;;
    *)
        echo "Invalid choice. Please run again and choose 1, 2, or 3."
        exit 1
        ;;
esac