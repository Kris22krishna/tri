from flask import Flask, render_template, request, redirect, url_for, session, send_file
import random
import time
import matplotlib.pyplot as plt
import seaborn as sns
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key in production

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'question_no' not in session:
        session['question_no'] = 0
        session['correct'] = 0
        session['times'] = []
        session['questions'] = []
        session['start_time'] = time.time()

    if session['question_no'] >= 10:
        return redirect(url_for('summary'))

    if request.method == 'POST':
        answer = int(request.form.get('answer', 0))
        correct_answer = session['questions'][-1]['ans']
        time_taken = time.time() - session['questions'][-1]['start']

        session['questions'][-1]['time'] = time_taken
        session['times'].append(time_taken)

        if answer == correct_answer:
            session['correct'] += 1
        session['question_no'] += 1

        return redirect(url_for('index'))

    a, b = random.randint(10, 99), random.randint(10, 99)
    ans = a + b
    session['questions'].append({'a': a, 'b': b, 'ans': ans, 'start': time.time()})

    return render_template('index.html', a=a, b=b, qno=session['question_no'] + 1)

@app.route('/summary')
def summary():
    total = session.get('question_no', 0)
    correct = session.get('correct', 0)
    times = session.get('times', [])

    avg_time = sum(times) / len(times) if times else 0
    session['summary_data'] = times

    return render_template('summary.html',
                           correct=correct,
                           total=total,
                           total_time=sum(times),
                           avg_time=avg_time)

@app.route('/chart')
def chart():
    times = session.get('summary_data', [])
    questions = [f"Q{i+1}" for i in range(len(times))]

    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 4))
    ax = sns.barplot(x=questions, y=times, palette="Blues_d")
    ax.set_title("Time Taken per Question")
    ax.set_ylabel("Time (s)")
    for i, v in enumerate(times):
        ax.text(i, v + 0.1, f"{v:.1f}", ha='center')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
