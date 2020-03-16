#!/usr/bin/env python3

import sys
import getopt
import sqlite3
import json
from datetime import datetime

# Напечатать в консоль справку по использованию
def usage():
    print('01_Extract.py -i <inputfile> -o <outputdb>')

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
def parse_line(j_line, tweets, locations, locations_map, urls):
    # Выберем только нужные нам атрибуты твита
    tweets.append((
        j_line['id']
        ,datetime.strptime(j_line['created_at'], '%a %b %d %H:%M:%S %z %Y')
        ,j_line['user']['screen_name']
        ,j_line['text']
        ,j_line['lang']
    ))
    # Запомним маппинг мест на ИД твитов
    if not(j_line.get('place') == None):
        temp = j_line['place'];
        locations.add((temp.get('name'), temp.get('country_code')))
        locations_map.append((temp.get('name'), temp.get('country_code'), j_line['id']))
    # Запомним все display_url
    parse_urls(j_line, 'extended_entities', 'media', urls)
    parse_urls(j_line, 'entities', 'urls', urls)

# Распарсить display_url в переданном поддереве
def parse_urls(j_line, subtree_nm, entity_nm, urls):
    if j_line.get(subtree_nm) == None: return
    temp = j_line[subtree_nm]
    if temp.get(entity_nm) == None: return
    for entry in temp[entity_nm]:
        urls.append((
            j_line['id']
            ,entry['display_url']
            ,'url' if entity_nm == 'urls' else entry['type']
        ))



##### Точка входа в процесс

def main(argv):
    # Распарсим аргументы
    try:
        opts, args = getopt.getopt(argv, "i:o:", ["ifile=", "odb="])
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

    if args_complete == 2:
        print('Input file is ', input_file)
        print('Output db is ', output_db)
    else:
        usage()
        sys.exit(3)

    del args_complete

    # Инициализируем ресурсы
    tweets = []
    locations = set()
    locations_map = []
    urls = []

    # Построчно будем читать файл
    with open(input_file, 'r', encoding='utf-8') as instream:
        for line in instream:
            j_line = json.loads(line)
            # Считаем, что если есть created_at, то это твит
            if not('created_at' in j_line): continue
            parse_line(j_line, tweets, locations, locations_map, urls)

    # Напарсились, теперь загрузим всё в базу
    db_conn = create_connection(output_db)
    if db_conn == None: sys.exit(4)

    # Заливаем справочник локаций
    with db_conn:
        db_conn.executemany(
            'INSERT or IGNORE INTO location (name, country_cd) VALUES (?, ?)'
            ,locations
        )
        del locations

    # Заливаем твиты
    with db_conn:
        db_conn.executemany(
            'INSERT or IGNORE INTO tweet (id, created_at, name, tweet_text, lang) VALUES (?, ?, ?, ?, ?)'
            ,tweets
        )
        del tweets

    # Заливаем урлы
    with db_conn:
        db_conn.executemany(
            'INSERT or IGNORE INTO url (tweet_id, display_url, type_cd) VALUES (?, ?, ?)'
            ,urls
        )
        del urls

    with db_conn:
        tmp_tbl_nm = 'tbl_temp_' + datetime.now().strftime("%y%m%d_%H%M%S")
        db_conn.execute(
            "CREATE TABLE {} (location_name NVARCHAR(1000), country_cd CHAR(2), tweet_id INTEGER);".format(tmp_tbl_nm)
        )
        db_conn.executemany(
            'INSERT INTO {} (location_name, country_cd, tweet_id) VALUES (?, ?, ?)'.format(tmp_tbl_nm)
            ,locations_map
        )
        db_conn.execute(
            """UPDATE tweet 
                SET location_id = (
                    SELECT t3.id
                    FROM {} t2
                    INNER JOIN location t3 ON (t3.name, t3.country_cd) = (t2.location_name, t2.country_cd)
                    WHERE tweet.id = t2.tweet_id
                )
                WHERE id IN (SELECT tweet_id FROM {}) and location_id is null
            ;""".format(tmp_tbl_nm, tmp_tbl_nm)
        )
        db_conn.execute(
            "DROP TABLE {} ;".format(tmp_tbl_nm)
        )
        del locations_map

    db_conn.close()

if __name__ == "__main__":
   main(sys.argv[1:])
