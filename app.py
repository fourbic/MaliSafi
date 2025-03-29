from flask import Flask, render_template, request, redirect, url_for, flash
from markdown import markdown
import os
import json
from dotenv import load_dotenv
from ai_agents.real_estate_agents import RealEstateAgentSystem

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'malisafi-development-key')

# Default property URLs
PROPERTY_URLS = [
    "https://www.knightfrank.com/property-for-sale/kenya",
    "https://www.buyrentkenya.com/property-for-sale",
    "https://www.pamgolding.co.za/property-search/properties-for-sale-kenya/119",
    "https://www.hassconsult.com/rentresidential",
]

# Sample search cards for Kenya
SEARCH_CARDS = [
    {"city": "Nairobi", "property_type": "Apartments", "max_price": "10,000,000"},
    {"city": "Mombasa", "property_type": "Beach Houses", "max_price": "25,000,000"},
    {"city": "Kisumu", "property_type": "Land", "max_price": "5,000,000"},
    {"city": "Nakuru", "property_type": "Family Homes", "max_price": "8,000,000"},
    {"city": "Eldoret", "property_type": "Commercial Spaces", "max_price": "15,000,000"},
    {"city": "Malindi", "property_type": "Vacation Homes", "max_price": "20,000,000"}
]

@app.route('/')
def index():
    """Render the home page with property search cards"""
    return render_template('index.html', search_cards=SEARCH_CARDS)

@app.route('/search', methods=['POST'])
def search():
    """Process the search form and run the property analysis"""
    city = request.form.get('city')
    property_type = request.form.get('property_type')
    max_price = request.form.get('max_price')
    
    if not city or not property_type or not max_price:
        flash('Please fill in all the search fields', 'error')
        return redirect(url_for('index'))
    
    try:
        # Initialize the agent system
        agent_system = RealEstateAgentSystem()
        
        # Run the analysis
        report_markdown = agent_system.run_analysis(
            city=city,
            property_type=property_type,
            max_price=max_price,
            property_urls=PROPERTY_URLS
        )
        
        # Convert markdown to HTML for display
        report_html = markdown(report_markdown)
        
        return render_template(
            'results.html', 
            report=report_html,
            city=city,
            property_type=property_type,
            max_price=max_price
        )
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
