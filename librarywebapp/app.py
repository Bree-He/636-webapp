from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect

app = Flask(__name__)

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@app.route("/")
def home():
    return render_template("base.html")

########这段是新加的-->
@app.route("/", methods=["POST"])
def searchbooks():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%"
    connection = getCursor()
    connection.execute("SELECT bookcopies.bookcopyid, bookcopies.format, books.booktitle, books.author,loans.loandate,\
                         loans.returned, adddate(loandate, interval 28 day) AS duedate\
                             FROM bookcopies\
                                 LEFT JOIN books ON bookcopies.bookid = books.bookid \
                                 LEFT JOIN loans ON bookcopies.bookcopyid = loans.bookcopyid\
                       WHERE books.booktitle LIKE %s OR books.author LIKE %s;",(searchterm, searchterm))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("searchlist.html", booklist = bookList)
########这段是新加的-->
######这段是做staff的
@app.route("/staff", methods=["GST", "POST"])
def staff():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%"
    connection = getCursor()
    connection.execute("SELECT bookcopies.bookcopyid, bookcopies.format, books.booktitle, books.author,loans.loandate,\
                         loans.returned, adddate(loandate, interval 28 day) AS duedate\
                             FROM bookcopies\
                                 LEFT JOIN books ON bookcopies.bookid = books.bookid \
                                 LEFT JOIN loans ON bookcopies.bookcopyid = loans.bookcopyid\
                       WHERE books.booktitle LIKE %s OR books.author LIKE %s;",(searchterm, searchterm))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("stafflist.html", booklist = bookList)


@app.route("/listbooks")
def listbooks():
    connection = getCursor()
    connection.execute("SELECT * FROM books;")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist = bookList)    

@app.route("/loanbook")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
inner join books on books.bookid = bookcopies.bookid
 WHERE bookcopyid not in (SELECT bookcopyid from loans where returned <> 1 or returned is NULL);"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("addloan.html", loandate = todaydate,borrowers = borrowerList, books= bookList)

@app.route("/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return redirect("/currentloans")

@app.route("/listborrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("borrowerlist.html", borrowerlist = borrowerList)

@app.route("/currentloans")
def currentloans():
    connection = getCursor()
    sql=""" select br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
            from books b
                inner join bookcopies bc on b.bookid = bc.bookid
                    inner join loans l on bc.bookcopyid = l.bookcopyid
                        inner join borrowers br on l.borrowerid = br.borrowerid
            order by br.familyname, br.firstname, l.loandate;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("currentloans.html", loanlist = loanList)