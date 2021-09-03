from flask import Flask, render_template, request, redirect
from data import Article
import pymysql
from pymongo import MongoClient
from flask_pymongo import PyMongo
from datetime import datetime 
from bson import ObjectId


db_connection = pymysql.connect(
    user = 'root',
    passwd = '1234',
    host = '127.0.0.1',
    db = 'modu',
    charset = 'utf8'
)

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://root:1234@cluster0.g4bac.mongodb.net/modu?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

mongo = PyMongo(app)
list_collection = mongo.db.list  # db뒤에 오는 list는 몽고 컴파스에 모두스키마에 만들어놓은 list 데이터 (python, ai bigprocesiing 의미함)


@app.route('/hello')
def hello_index():
    name = 'LEE'
    return render_template('index.html', data=name)

@app.route('/articles', methods=['GET', 'POST'])
def articles():
    cursor = db_connection.cursor()
    sql = 'SELECT * FROM list;'
    cursor.execute(sql)
    topics = cursor.fetchall()
    print(topics)
    return render_template('articles.html', data = topics)




# list.insert_one() # 몽고디비 플라스크 데이터를 저장하기  
@app.route('/articles_mongo', methods=['GET', 'POST'])
def articles_mongo():
  
    data = list_collection.find()
    print(data)
    return render_template('articles_mongo.html', articles = data)


@app.route('/add_article', methods=['GET', 'POST'])
def add_articles():
    if request.method == "GET":
        return render_template('add_article.html')

    else:
        title = request.form['title'] 
        desc = request.form['desc'] 
        author = request.form['author']
        
        # mongodb insert
        mongo_insert_data = {
            "title":title,
            "description":desc,
            "author":author,
            "create_at":datetime.now()
             }
        list_collection.insert_one(mongo_insert_data)

        # mysql insert 
        cursor = db_connection.cursor()
        sql = f"INSERT INTO list (title, description, author) VALUES ('{title}', '{desc}', '{author}');" 
        cursor.execute(sql)
        db_connection.commit()
        return redirect('/articles')



@app.route('/delete/<ids>', methods=["GET","POST"])
def delete(ids):
    # mysql delete
    cursor = db_connection.cursor()
    sql = f"DELETE FROM list WHERE (id = {ids});"
    cursor.execute(sql)
    db_connection.commit()

    return redirect('/articles')

@app.route('/<id>/delete', methods=["GET","POST"])
def delete_mongo(id):
    # mongodb delete
    list_collection.delete_one({ "_id":ObjectId(id) })
    return redirect('/articles_mongo')


@app.route('/detail/<ids>', methods=["GET", "POST"])
def detail(ids):
    cursor = db_connection.cursor()
    sql = f'SELECT * FROM list WHERE id={int(ids)};' 
    cursor.execute(sql)
    topic = cursor.fetchone()

    return render_template('article.html', article=topic)

#몽고
@app.route('/<id>/detail_mongo', methods=["GET","POST"])
def detail_mongo(id):
    topic = list_collection.find_one({ "_id":ObjectId(id)})
    print(topic)
    return render_template('article_mongo.html', article=topic)

#sql
@app.route('/edit/<ids>', methods=["GET", "POST"])
def edit_article(ids):
    if request.method == 'GET':
        cursor = db_connection.cursor()
        sql = f'SELECT * FROM list WHERE id={int(ids)};'   
        cursor.execute(sql)
        topic = cursor.fetchone()  
        print(topic)
        return render_template('edit_article.html', article = topic)

    else:
        title = request.form["title"]
        desc = request.form["desc"]
        author = request.form["author"]

        cursor = db_connection.cursor()
        sql = f"UPDATE list SET title= '{title}', description = '{desc}' ,author='{author}' WHERE (id = {int(ids)});"
        cursor.execute(sql)
        db_connection.commit()
        return redirect('/articles')

#몽고
@app.route('/<id>/edit', methods=["GET", "POST"])
def edit_article_mongo(id):
    if request.method == "GET":
        topic = list_collection.find_one({ "_id":ObjectId(id)})
        print(topic)
        return render_template('edit_article_mongo.html', article=topic)

    else:
        title = request.form["title"]
        desc = request.form["desc"]
        author = request.form["author"]


        myquery = {
            "_id": ObjectId(id)
            }
        newvalues ={ "$set": { "title":title, "description":desc, "author":author, "create_at":datetime.now()}}
        list_collection.update_one(myquery,newvalues)
        return redirect('/articles_mongo')











if __name__ == '__main__':
    app.run(debug=True)