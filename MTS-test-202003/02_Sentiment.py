#!/usr/bin/env python3

import sys
import getopt
import sqlite3
import json
from datetime import datetime

# Напечатать в консоль справку по использованию
def usage():
    print('02_Sentiment.py -s <sentiment_file> -i <input_file> -o <output_db>')

# Создать соединение с БД
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

# Разобрать очередную строку, полученную на вход
def parse_line(j_line, tweets, sentiments):
    # Выберем только нужные нам атрибуты твита
    exploded_tweet = j_line['text'].lower().split()
    matches = 0
    sentiment = 0
    for word in exploded_tweet:
        word = word.rstrip('#')
        if (sentiments.get(word) == None): continue
        matches += 1
        sentiment += sentiments[word];
    if (matches > 0):
        sentiment = float(sentiment) / matches
    tweets.append((j_line['id'], sentiment))



##### Точка входа в процесс

def main(argv):
    # Распарсим аргументы
    try:
        opts, args = getopt.getopt(argv, "s:i:o:", ["senfile=", "ifile=", "odb="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Флаг, что все обязательные аргументы поступили на вход
    args_complete = 0

    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            input_file = arg
            args_complete += 1
        elif opt in ("-o", "--odb"):
            output_db = arg
            args_complete += 1
        elif opt in ("-s", "--senfile"):
            sentiment_file = arg
            args_complete += 1

    if args_complete == 3:
        print('Input file is ', input_file)
        print('Output db is ', output_db)
        print('Sentiment file is ', sentiment_file)
    else:
        usage()
        sys.exit(3)

    del args_complete

    # Инициализируем ресурсы
    tweets = []
    sentiments = {}

    # Считаем словарь настроений
    with open(sentiment_file, 'r', encoding='utf-8') as instream:
        for line in instream:
            temp = line.split('\t', 1)
            sentiments[temp[0]] = int(temp[1].rstrip())


    # Построчно будем читать файл с твитами
    with open(input_file, 'r', encoding='utf-8') as instream:
        for line in instream:
            j_line = json.loads(line)
            # Считаем, что если есть created_at, то это твит
            if not('created_at' in j_line): continue
            parse_line(j_line, tweets, sentiments)

    # Напарсились, теперь загрузим всё в базу
    db_conn = create_connection(output_db)
    if db_conn == None: sys.exit(4)

    with db_conn:
        tmp_tbl_nm = 'tbl_temp_' + datetime.now().strftime("%y%m%d_%H%M%S")
        db_conn.execute(
            "CREATE TABLE {} (tweet_id INTEGER, tweet_sentiment FLOAT);".format(tmp_tbl_nm)
        )
        db_conn.executemany(
            'INSERT INTO {} (tweet_id, tweet_sentiment) VALUES (?, ?)'.format(tmp_tbl_nm)
            ,tweets
        )
        db_conn.execute(
            """UPDATE tweet 
                SET tweet_sentiment = (
                    SELECT t2.tweet_sentiment
                    FROM {} t2
                    WHERE tweet.id = t2.tweet_id
                )
                WHERE id IN (SELECT tweet_id FROM {})
            ;""".format(tmp_tbl_nm, tmp_tbl_nm)
        )
        db_conn.execute(
            "DROP TABLE {} ;".format(tmp_tbl_nm)
        )
        del tweets

    db_conn.close()


if __name__ == "__main__":
   main(sys.argv[1:])
