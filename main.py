from flask import Flask, request, render_template_string
import re
from datetime import datetime

app = Flask(__name__)

def parse_timecode(timecode):
    return datetime.strptime(timecode, '%H:%M:%S')

def find_non_monotonic_timecodes(transcript):
    timecode_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    non_monotonic = []
    previous_time = None
    lines = transcript.splitlines()
    current_timecode = None
    
    for line in lines:
        match = timecode_pattern.match(line.strip())
        if match:
            current_timecode = match.group(0)
            current_time = parse_timecode(current_timecode)
            if previous_time and current_time <= previous_time:
                non_monotonic.append(current_timecode)
            previous_time = current_time
    return non_monotonic

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    is_post = request.method == 'POST'
    if is_post:
        transcript = request.form['transcript']
        result = find_non_monotonic_timecodes(transcript)
    
    html_form = """
    <!doctype html>
    <title>Check Monotonic Timecodes</title>
    <h1>Submit Transcript</h1>
    <form method=post>
      <textarea name="transcript" rows="10" cols="50"></textarea><br>
      <input type=submit value="Check">
    </form>
    <h2>Result:</h2>
    {% if result %}
    <p>Non-monotonic timecodes found:</p>
    <ul>
      {% for tc in result %}
        <li>{{ tc }}</li>
      {% endfor %}
    </ul>
    {% elif is_post %}
    <p>All timecodes are monotonically increasing</p>
    {% else %}
    <p>No input provided.</p>
    {% endif %}
    """
    return render_template_string(html_form, result=result, is_post=is_post)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
