from flask import Flask, render_template, request, redirect, url_for
from news_parser import extract
from json_handler import get_texts, get_news_data, get_titles, get_plot_data, update_plot_data, remove_plot_data, save_plot_data
from model_handler import predict_texts
import json
from datetime import datetime


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    simulate_flag = False

    if request.method == 'POST':
        if 'extract' in request.form:
            search_query = request.form.get('search_query')
            news_count = request.form.get('news_count')

            if search_query and news_count:
                news_count = int(news_count)
                extract(search_query, news_count)

            return redirect(url_for('index'))

        elif 'plot' in request.form:
            texts, dates = get_texts()
            titles = get_titles()

            outputs = predict_texts(texts)
            outputs = [float(output) for output in outputs]

            save_plot_data(outputs, dates, titles)

        elif 'simulate' in request.form:
            news_simulate = request.form.get('simulated_text')

            if news_simulate:
                model_output = float(predict_texts([news_simulate])[0])
                current_date = datetime.now().strftime("%d.%m.%Y")
                title = news_simulate.split('.')[0]

                update_plot_data({
                    'predictions': model_output,
                    'dates': current_date,
                    'titles': title
                })

                simulate_flag = True

    news_data = get_news_data()
    plot_data = get_plot_data()

    if simulate_flag:
        remove_plot_data()

    return render_template('index.html', plot_data=json.dumps(plot_data), news_data=news_data)



if __name__ == '__main__':
    app.run(debug=True)