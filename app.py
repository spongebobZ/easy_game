from flask import Flask, render_template, jsonify, request
import tools

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def goto_search():
    return render_template('search.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']
    last_word = request.form['backword']
    last_submit_word = request.form['sendedword']
    result_word = last_word
    if last_word and keyword[:1] != last_word[-1:]:
        msg = '开头与旧成语末尾不同'
        print(last_word,keyword)
    else:
        iscy = tools.check_cy(keyword)
        if iscy == 0:
            result_word = tools.search_cy(keyword[-1:])
            if result_word:
                msg = '轮到你'
            else:
                msg = '我认输了'
            last_submit_word = keyword
        elif iscy == -1:
            msg = keyword + '：不是成语'
        elif iscy == -2:
            msg = keyword + '：非4个字词语'
        else:
            msg = '未知错误'
    # return jsonify({'search_result': result_word, 'search_message': msg})
    return render_template('search.html', backword=result_word, search_message=msg, sendedword=last_submit_word)

@app.route('/reset_search', methods=['GET'])
def reset_search():
    return render_template('search.html')


if __name__ == '__main__':
    app.run(host='192.168.1.110',port=5656)
