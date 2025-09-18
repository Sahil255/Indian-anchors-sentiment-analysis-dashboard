import requests
import json
from datetime import datetime, timedelta
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY') or 'your_openrouter_key_here'

API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Anchor list
anchors = [
    {'name': 'Rajat Sharma', 'handle': 'RajatSharmaLive', 'x_url': 'https://x.com/RajatSharmaLive'},
    {'name': 'Sudhir Chaudhary', 'handle': 'sudhirchaudhary', 'x_url': 'https://x.com/sudhirchaudhary'},
    {'name': 'Anjana Om Kashyap', 'handle': 'anjanaomkashyap', 'x_url': 'https://x.com/anjanaomkashyap'},
    {'name': 'Rubika Liyaquat', 'handle': 'RubikaLiyaquat', 'x_url': 'https://x.com/RubikaLiyaquat'},
    {'name': 'Navika Kumar', 'handle': 'navikakumar', 'x_url': 'https://x.com/navikakumar'},
    {'name': 'Amish Devgan', 'handle': 'AMISHDEVGAN', 'x_url': 'https://x.com/AMISHDEVGAN'},
    {'name': 'Rajdeep Sardesai', 'handle': 'sardesairajdeep', 'x_url': 'https://x.com/sardesairajdeep'},
    {'name': 'Barkha Dutt', 'handle': 'BDUTT', 'x_url': 'https://x.com/BDUTT'},
    {'name': 'Ravish Kumar', 'handle': 'ravish_journo', 'x_url': 'https://x.com/ravish_journo'},
    {'name': 'Rahul Kanwal', 'handle': 'rahulkanwal', 'x_url': 'https://x.com/rahulkanwal'}
]

def fetch_and_analyze_tweets(handle, date):
    prompt = f"""
    Fetch upto 20 public X posts from @{handle} posted on {date.strftime('%Y-%m-%d')} mentioning Modi, BJP, government, or PM.
    Analyze each post for sentiment: pro (praise/defense of Modi/BJP), anti (criticism), neutral (factual/promo), questions (direct queries to govt).
    Use keywords: pro ('praise', 'triumph', 'modi great', 'bjp win'), anti ('criticism', 'scandal', 'adani'), questions ('why', 'how', '?'), neutral (else).
    Consider context/sarcasm for accuracy. Return JSON:
    {{
        "posts": [{{"text": str, "sentiment": str}}],
        "counts": {{"pro": int, "anti": int, "neutral": int, "questions": int}}
    }}
    """
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://your-app-domain.com',  # Optional for OpenRouter analytics
        'X-Title': 'Sentiment Dashboard'  # Optional for OpenRouter analytics
    }
    payload = {
        'model': 'x-ai/grok-4',  # Use 'xai/grok-3' for free tier if needed
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 4000,
        'response_format': {
            'type': 'json_schema',
            'json_schema': {
                'name': 'sentiment_analysis',
                'strict': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'posts': {'type': 'array', 'items': {'type': 'object', 'properties': {
                            'text': {'type': 'string'}, 'sentiment': {'type': 'string', 'enum': ['pro', 'anti', 'neutral', 'questions']}
                        }, 'required': ['text', 'sentiment'], 'additionalProperties': False}},
                        'counts': {'type': 'object', 'properties': {
                            'pro': {'type': 'integer'}, 'anti': {'type': 'integer'},
                            'neutral': {'type': 'integer'}, 'questions': {'type': 'integer'}
                        }, 'required': ['pro', 'anti', 'neutral', 'questions'], 'additionalProperties': False}
                    },
                    'required': ['posts', 'counts'],
                    'additionalProperties': False
                }
            }
        }
    }
    # try:
    #     response = requests.post(API_URL, headers=headers, json=payload)
    #     response.raise_for_status()
    #     content = response.json()['choices'][0]['message']['content']
    #     # Parse JSON from content
    #     result = json.loads(content)
    #     return result
    # except requests.exceptions.HTTPError as e:
    #     print(f"HTTP Error for {handle}: {e}")
    #     print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
    #     return {'posts': [], 'counts': {'pro': 0, 'anti': 0, 'neutral': 0, 'questions': 0}}
    # except json.JSONDecodeError as e:
    #     print(f"JSON Parse Error for {handle}: {e}")
    #     print(f"Content: {content if 'content' in locals() else 'No content'}")
    #     return {'posts': [], 'counts': {'pro': 0, 'anti': 0, 'neutral': 0, 'questions': 0}}
    # except Exception as e:
    #     print(f"Unexpected Error for {handle}: {e}")
    #     return {'posts': [], 'counts': {'pro': 0, 'anti': 0, 'neutral': 0, 'questions': 0}}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        print("response {response}")
        return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Error for {handle}: {e}")
        return {'posts': [], 'counts': {'pro': 0, 'anti': 0, 'neutral': 0, 'questions': 0}}

# def validate_sentiment(text, grok_sentiment):
#     analyzer = SentimentIntensityAnalyzer()
#     score = analyzer.polarity_scores(text)
#     pro_keywords = ['modi', 'bjp', 'praise', 'triumph']
#     anti_keywords = ['criticism', 'scandal', 'adani']
#     question_keywords = ['why', 'how', '?']
#     text_lower = text.lower()
#     if any(kw in text_lower for kw in question_keywords): return 'questions'
#     if any(kw in text_lower for kw in pro_keywords) and score['compound'] > 0.05: return 'pro'
#     if any(kw in text_lower for kw in anti_keywords) and score['compound'] < -0.05: return 'anti'
#     return 'neutral'

def load_cache():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'start_date': '2025-07-01', 'end_date': '2025-07-01', 'anchors': {}}

def save_cache(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)

def escape_js_string(s):
    """Escape special characters for JavaScript string."""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')

def generate_html(data, pro_pct, anti_pct, neutral_pct, winner, winner_score):
    # Format postsData as a JavaScript object string
    posts_data = {}
    for a in anchors:
        if data['anchors'][a['handle']]['posts']:
            posts_html = ''.join(
                f'<p class=\\"{p["sentiment"]}\\">{p["sentiment"].capitalize()}: {escape_js_string(p["text"][:50])}...</p>'
                for p in data['anchors'][a['handle']]['posts'][:3]
            )
            posts_data[a['name']] = f'<div class="posts">{posts_html}</div>'
    
    posts_data_js = '{\n' + ',\n'.join(
        f'    "{k}": "{escape_js_string(v)}"' for k, v in posts_data.items()
    ) + '\n}'

    pro_value = winner.get('pro', 0)  # Use .get() to provide a default value (e.g., 0) if the key is missing.
    questions_value = winner.get('questions', 0)
    total_value = winner.get('total', 1) # Avoid division by zero with a fallback value

    # Calculate the total posts first to check for zero
    total_posts = sum(a['total'] for a in data['anchors'].values())

    if total_posts == 0:
        questions_pct = 0
    else:
        total_questions = sum(a['questions'] for a in data['anchors'].values())
        questions_pct = (total_questions / total_posts) * 100

    # <p>{pro_pct:.1f}% pro bias shows favoritism (e.g., Modi's diplomacy), but {neutral_pct:.1f}% neutral reflects promos. Anti ({anti_pct:.1f}%) from critics like Rajdeep/Barkha. Questions ({sum(a['questions'] for a in data['anchors'].values())/sum(a['total'] for a in data['anchors'].values())*100:.1f}%) rare, indicating low scrutiny. TV anchors (Sudhir/Rajat) lean pro; independents balance.</p>

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Indian Media Anchors Sentiment Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1 {{ text-align: center; color: #333; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center; flex: 1; margin: 0 10px; }}
            .winner-section {{ background: linear-gradient(135deg, #4CAF50, #2e7d32); color: white; padding: 25px; border-radius: 12px; margin: 20px 0; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
            .winner-section h2 {{ margin: 0; font-size: 1.8em; }}
            .winner-score {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
            .winner-section a {{ color: #bbdefb; font-weight: bold; }}
            .winner-section a:hover {{ text-decoration: underline; }}
            canvas {{ max-height: 400px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .filter {{ margin: 20px 0; }}
            .filter select {{ margin: 5px; padding: 8px; border-radius: 5px; }}
            .critique {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .posts {{ display: none; margin-top: 10px; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
            .pro {{ color: green; }}
            .anti {{ color: red; }}
            .neutral {{ color: blue; }}
            a {{ color: #1DA1F2; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .clickable {{ cursor: pointer; color: #1DA1F2; }}
            .clickable:hover {{ text-decoration: underline; }}
            @media (max-width: 768px) {{ .stats {{ flex-direction: column; }} .stat-box {{ margin: 10px 0; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Indian Media Anchors Sentiment Analysis Dashboard</h1>
            <p>{data['start_date']} - {data['end_date']} (~{sum(a['total'] for a in data['anchors'].values())} posts analyzed). Static data; refreshes every 1-2 days. Sentiments: pro (Modi/BJP praise), anti (criticism), neutral (factual/promo), questions (queries).</p>
            
            <div class="stats">
                <div class="stat-box">
                    <h3>Pro-Government</h3>
                    <p>{pro_pct:.1f}% ({sum(a['pro'] for a in data['anchors'].values())})</p>
                </div>
                <div class="stat-box">
                    <h3>Anti-Government</h3>
                    <p>{anti_pct:.1f}% ({sum(a['anti'] for a in data['anchors'].values())})</p>
                </div>
                <div class="stat-box">
                    <h3>Neutral/Questions</h3>
                    <p>{neutral_pct:.1f}% ({sum(a['neutral'] + a['questions'] for a in data['anchors'].values())})</p>
                </div>
            </div>
            
            <div class="winner-section">
                <h2>Most Pro-Government Anchor</h2>
                <p><strong>{winner['name']} (<a href="{winner['x_url']}">@{winner['handle']}</a>)</strong></p>
                <p class="winner-score">Score: {winner_score:.1f}</p>
                <p>Algorithm: (Pro % - Questions %) = ({pro_value/total_value*100:.1f}% - {questions_value/total_value*100:.1f}%) | Rationale: {pro_value}/{total_value} posts pro; {questions_value} questions.</p>
            </div>
            
            <canvas id="sentimentChart"></canvas>
            
            <div class="filter">
                <label>Filter by Sentiment: </label>
                <select id="sentimentFilter">
                    <option value="all">All</option>
                    <option value="pro">Pro-Government</option>
                    <option value="anti">Anti-Government</option>
                    <option value="neutral">Neutral/Questions</option>
                </select>
                <label>Filter by Anchor: </label>
                <select id="anchorFilter">
                    <option value="all">All Anchors</option>
                    {"".join(f'<option value="{a["name"]}">{a["name"]}</option>' for a in anchors)}
                </select>
            </div>
            
            <table id="anchorsTable">
                <thead>
                    <tr>
                        <th>Anchor</th>
                        <th>Handle</th>
                        <th>Pro-Govt</th>
                        <th>Anti-Govt</th>
                        <th>Neutral</th>
                        <th>Questions</th>
                        <th>Key Examples</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'<tr data-anchor="{a["name"]}" data-sentiment="{data["anchors"][a["handle"]]["sentiment"]}"><td>{a["name"]}</td><td><a href="{a["x_url"]}">@{a["handle"]}</a></td><td class="pro">{data["anchors"][a["handle"]]["pro"]}</td><td class="anti">{data["anchors"][a["handle"]]["anti"]}</td><td class="neutral">{data["anchors"][a["handle"]]["neutral"]}</td><td>{data["anchors"][a["handle"]]["questions"]}</td><td class="clickable" onclick="showPosts(\'{a["name"]}\')">View Examples</td></tr>' for a in anchors)}
                </tbody>
            </table>
            
            <div id="postsSection"></div>
            
            <div class="critique">
                <h3>Critique of Indian Media Anchors</h3>
                <p>... Questions ({questions_pct:.1f}%) rare, indicating low scrutiny ...</p>
                <p>{pro_pct:.1f}% pro bias shows favoritism (e.g., Modi's diplomacy), but {neutral_pct:.1f}% neutral reflects promos. Anti ({anti_pct:.1f}%) from critics like Rajdeep/Barkha. Questions  ({questions_pct:.1f}%) rare, indicating low scrutiny. TV anchors (Sudhir/Rajat) lean pro; independents balance.</p>
                
            </div>
        </div>
        
        <script>
            const ctx = document.getElementById('sentimentChart').getContext('2d');
            const chart = new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: ['Pro-Government', 'Anti-Government', 'Neutral/Questions'],
                    datasets: [{{
                        data: [{pro_pct:.1f}, {anti_pct:.1f}, {neutral_pct:.1f}],
                        backgroundColor: ['#4CAF50', '#f44336', '#2196F3']
                    }}]
                }},
                options: {{ responsive: true }}
            }});
            
            document.getElementById('sentimentFilter').addEventListener('change', filterTable);
            document.getElementById('anchorFilter').addEventListener('change', filterTable);
            
            function filterTable() {{
                const sentiment = document.getElementById('sentimentFilter').value;
                const anchor = document.getElementById('anchorFilter').value;
                const rows = document.querySelectorAll('#anchorsTable tbody tr');
                
                rows.forEach(row => {{
                    const rowSentiment = row.dataset.sentiment;
                    const rowAnchor = row.dataset.anchor;
                    let show = true;
                    if (sentiment !== 'all' && rowSentiment !== sentiment) show = false;
                    if (anchor !== 'all' && rowAnchor !== anchor) show = false;
                    row.style.display = show ? '' : 'none';
                }});
            }}
            
            const postsData = {posts_data_js};
            
            function showPosts(anchor) {{
                const section = document.getElementById('postsSection');
                section.innerHTML = postsData[anchor] || '<p>No posts available.</p>';
                section.style.display = 'block';
            }}
        </script>
    </body>
    </html>
    """
    with open('media-dashboard.html', 'w') as f:
        f.write(html)
    print("Dashboard updated now!!")

# Mock data for testing (replace with real API calls)
mock_data = {
    'start_date': '2025-07-01',
    'end_date': '2025-09-18',
    'anchors': {
        'RajatSharmaLive': {'pro': 7, 'anti': 0, 'neutral': 9, 'questions': 0, 'total': 16, 'sentiment': 'neutral', 'posts': [{'text': 'Modi’s war against infiltrators...', 'sentiment': 'pro'}, {'text': 'Modi@75: Love from all over...', 'sentiment': 'neutral'}]},
        'sudhirchaudhary': {'pro': 5, 'anti': 0, 'neutral': 6, 'questions': 0, 'total': 11, 'sentiment': 'neutral', 'posts': [{'text': 'BOSS of global politics...', 'sentiment': 'pro'}, {'text': 'Tonight at 9 pm...', 'sentiment': 'neutral'}]},
        'anjanaomkashyap': {'pro': 0, 'anti': 0, 'neutral': 2, 'questions': 0, 'total': 2, 'sentiment': 'neutral', 'posts': [{'text': 'Modi turns 75...', 'sentiment': 'neutral'}]},
        'RubikaLiyaquat': {'pro': 0, 'anti': 0, 'neutral': 1, 'questions': 0, 'total': 1, 'sentiment': 'neutral', 'posts': [{'text': 'Trump: My friend Modi...', 'sentiment': 'neutral'}]},
        'navikakumar': {'pro': 2, 'anti': 0, 'neutral': 4, 'questions': 0, 'total': 6, 'sentiment': 'neutral', 'posts': [{'text': 'First meeting with PM...', 'sentiment': 'pro'}, {'text': 'Congress’s rising star...', 'sentiment': 'neutral'}]},
        'AMISHDEVGAN': {'pro': 0, 'anti': 0, 'neutral': 10, 'questions': 0, 'total': 10, 'sentiment': 'neutral', 'posts': [{'text': 'Trump vs India...', 'sentiment': 'neutral'}]},
        'sardesairajdeep': {'pro': 6, 'anti': 2, 'neutral': 32, 'questions': 0, 'total': 40, 'sentiment': 'neutral', 'posts': [{'text': 'Happy birthday call...', 'sentiment': 'pro'}, {'text': 'Modi birthday cult...', 'sentiment': 'anti'}, {'text': 'Cong WON Aland...', 'sentiment': 'neutral'}]},
        'BDUTT': {'pro': 4, 'anti': 4, 'neutral': 27, 'questions': 0, 'total': 35, 'sentiment': 'neutral', 'posts': [{'text': 'Interviewing PM Modi...', 'sentiment': 'pro'}, {'text': 'Trump is unstable...', 'sentiment': 'anti'}, {'text': 'Trump’s call to Modi...', 'sentiment': 'neutral'}]},
        'ravish_journo': {'pro': 0, 'anti': 0, 'neutral': 1, 'questions': 0, 'total': 1, 'sentiment': 'neutral', 'posts': [{'text': 'Disturbing news...', 'sentiment': 'neutral'}]},
        'rahulkanwal': {'pro': 0, 'anti': 0, 'neutral': 3, 'questions': 0, 'total': 3, 'sentiment': 'neutral', 'posts': [{'text': 'Finance Minister answers...', 'sentiment': 'neutral'}]}
    }
}

# Main logic
# today = datetime.now().strftime('%Y-%m-%d')
today_date = datetime.now()
yesterday = today_date - timedelta(days=2)

# Format yesterday's date as 'YYYY-MM-DD'
today = yesterday.strftime('%Y-%m-%d')

cache = load_cache()
if cache['end_date'] != today:
    for anchor in anchors:
        handle = anchor['handle']
        result = fetch_and_analyze_tweets(handle, datetime.now())
        # result = mock_data
        print("fecthing...")
        if handle not in cache['anchors']:
            cache['anchors'][handle] = {'pro': 0, 'anti': 0, 'neutral': 0, 'questions': 0, 'total': 0, 'sentiment': 'neutral', 'posts': []}
        cache['anchors'][handle]['pro'] += result['counts']['pro']
        cache['anchors'][handle]['anti'] += result['counts']['anti']
        cache['anchors'][handle]['neutral'] += result['counts']['neutral']
        cache['anchors'][handle]['questions'] += result['counts']['questions']
        cache['anchors'][handle]['total'] += sum(result['counts'].values())
        cache['anchors'][handle]['posts'].extend(result['posts'][:3])  # Store up to 3 samples
        cache['anchors'][handle]['sentiment'] = 'pro' if cache['anchors'][handle]['pro'] > cache['anchors'][handle]['anti'] and cache['anchors'][handle]['pro'] > cache['anchors'][handle]['neutral'] else 'anti' if cache['anchors'][handle]['anti'] > cache['anchors'][handle]['pro'] and cache['anchors'][handle]['anti'] > cache['anchors'][handle]['neutral'] else 'neutral'
    cache['end_date'] = today
    save_cache(cache)

# Calculate aggregates
total = sum(a['total'] for a in cache['anchors'].values())
pro_pct = sum(a['pro'] for a in cache['anchors'].values()) / total * 100 if total > 0 else 0
anti_pct = sum(a['anti'] for a in cache['anchors'].values()) / total * 100 if total > 0 else 0
neutral_pct = sum(a['neutral'] + a['questions'] for a in cache['anchors'].values()) / total * 100 if total > 0 else 0

# Determine winner
winner = max(anchors, key=lambda x: (cache['anchors'][x['handle']]['pro']/cache['anchors'][x['handle']]['total']*100 - cache['anchors'][x['handle']]['questions']/cache['anchors'][x['handle']]['total']*100) if cache['anchors'][x['handle']]['total'] > 0 else 0)
# winner_score = (cache['anchors'][winner['handle']]['pro']/winner['total']*100 - cache['anchors'][winner['handle']]['questions']/winner['total']*100) if cache['anchors'][winner['handle']]['total'] > 0 else 0
winner_score = 99
# Generate HTML
generate_html(cache, pro_pct, anti_pct, neutral_pct, winner, winner_score)