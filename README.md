# MaliSafi - Multi AI Agent Crew => Real Estate

MaliSafi is a web application that uses AI agents to find, analyze, and report on property.
## Features

- AI-powered property search across multiple real estate websites
- Comparative market analysis of property investment opportunities
- Location-based price trend analysis
- Comprehensive property reports with recommendations

## Technology Stack

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI**: CrewAI multi-agent framework, LangChain
- **Data**: Web scraping from major Kenyan real estate websites

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/fourbic/malisafi.git
   cd malisafi
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

## Usage

1. Test it out on the notebook and for a webapp the project uses a Flask application:
   Notebook can be found here 
   ```
   /notebook/realEstate_MultiAgent_Crew.ipynb
   ```

2. Flask runs on your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Enter your property search criteria or select from the popular search cards on the homepage.

4. Wait for the AI agents to analyze properties and generate a report.

## Project Structure

```
MaliSafi/
├── ai_agents/                # AI agent modules
│   ├── __init__.py
│   └── real_estate_agents.py
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
│       └── logo.svg
├── templates/                # HTML templates
│   ├── index.html
│   ├── results.html
│   └── about.html
├── app.py                    # Main Flask application
├── .env                      # Environment variables (not in version control)
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project uses the CrewAI framework for multi-agent orchestration.