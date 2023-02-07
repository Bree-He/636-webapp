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
def public():
    return render_template("public.html")

########这段是新加的-->
@app.route("/search", methods=["POST"])
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
@app.route("/staff")
def staff():
    return render_template("base.html")

@app.route("/staffsearch", methods=["POST"])
def staffsearch():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("SELECT bookcopies.bookcopyid, bookcopies.format, books.booktitle, books.author,loans.loandate,\
                         loans.returned, adddate(loandate, interval 28 day) AS duedate\
                             FROM bookcopies\
                                 LEFT JOIN books ON bookcopies.bookid = books.bookid \
                                 LEFT JOIN loans ON bookcopies.bookcopyid = loans.bookcopyid\
                       WHERE books.booktitle LIKE %s OR books.author LIKE %s;",(searchterm, searchterm))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("staffsearch.html", booklist = bookList)


##############this route is display all availability of all copies of a book.

@app.route("/staffbc")
def staffbc():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("SELECT bookcopies.bookcopyid, bookcopies.format, books.booktitle, books.author,loans.loandate,\
                         loans.returned, adddate(loandate, interval 28 day) AS duedate\
                             FROM bookcopies\
                                 LEFT JOIN books ON bookcopies.bookid = books.bookid \
                                 LEFT JOIN loans ON bookcopies.bookcopyid = loans.bookcopyid\
                       WHERE books.booktitle LIKE %s OR books.author LIKE %s;",(searchterm, searchterm))
    bookList = connection.fetchall()
    print(bookList)
    return render_template("staffbc.html", booklist = bookList)

##########public interface list all avaliable book(bookcopies)
@app.route("/booklist")
def listbooks():
    connection = getCursor()
    connection.execute("SELECT DISTINCT bookcopies.bookcopyid, books.booktitle, books.author, \
                        books.yearofpublication, books.category, loans.returned \
                            from bookcopies \
                                left join books on bookcopies.bookid = books.bookid \
                                    left join loans on bookcopies.bookcopyid = loans.bookcopyid \
                                        where returned = 1 or returned is null;")
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
#######return a book
@app.route("/returnbook")
def returnbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    sql = "SELECT * FROM loans WHERE returned = 1;"
    connection.execute(sql)  
    loanList = connection.fetchall()
    return render_template("returnloan.html", returndate = todaydate, loans = loanList)
@app.route("/loan/return", methods=["POST"])
def returnloan():
    loanid = request.form.get('loanid')
    bookcopyid = request.form.get('bookcopyid')  
    borrowerid= request.form.get('borrowerid')  
    loandate = request.form.get('loandate')   
    cur = getCursor()
    cur.execute("update loans set loans.returned = '1' where loanid = %s", (loanid,))
    return redirect("/currentloans")





@app.route("/listborrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("borrowerlist.html", borrowerlist = borrowerList)

#####following is create a table for search borrowers by name or by id
@app.route("/searchborrower", methods=["POST"])
def searchborrowers():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers WHERE borrowers.firstname LIKE %s OR borrowers.familyname LIKE %s OR borrowers.borrowerid LIKE %s;",(searchterm, searchterm, searchterm,))
    borrowerList = connection.fetchall()
    return render_template("borrower_search.html", borrowerlist = borrowerList)

#########following function is for retrieve the borrower details from the database, update the details based on the user input, and save it back to database
@app.route("/borrowerupdate", methods=["GET", "POST"])
def updateborrower():
    searchterm = request.form.get('borrowerid')
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers WHERE borrowers.borrowerid LIKE %s ;",(searchterm,))
    borrower = connection.fetchall()
    if borrower:
        return render_template("borrower_update.html", borrower = borrower)
    return render_template("borrower_update.html")

@app.route("/borrowerup1", methods=["POST"])
def update1borrower():
    searchterm = request.form.get('search')
    borrowerid = request.form.get('borrowerid') 
    firstname = request.form.get('firstname')
    familyname = request.form.get('familyname')
    dateofbirth = request.form.get('dateofbirth')
    housenumbername = request.form.get('housenumbername')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('postalcode')
  
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("update borrowers set firstname=%s, familyname=%s, dateofbirth=%s, housenumbername=%s, street=%s, town=%s, city=%s,postalcode=%s \
        WHERE (`borrowerid`=%s);",(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode, borrowerid,))
    borrowerList = connection.fetchall()
    return render_template("borrower_update.html", borrowerlist = borrowerList)

@app.route("/borrowerup2", methods=["POST"])
def update1borrower2():
    searchterm = request.form.get('search')
    borrowerid = request.form.get('borrowerid') 
    firstname = request.form.get('firstname')
    familyname = request.form.get('familyname')
    dateofbirth = request.form.get('dateofbirth')
    housenumbername = request.form.get('housenumbername')
    street = request.form.get('street')
    town = request.form.get('town')
    city = request.form.get('city')
    postalcode = request.form.get('postalcode')
  
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("update borrowers set firstname=%s, familyname=%s, dateofbirth=%s, housenumbername=%s, street=%s, town=%s, city=%s,postalcode=%s \
        WHERE (`borrowerid`=%s);",(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode, borrowerid,))
    borrowerList = connection.fetchall()
    return render_template("borrower_update.html", borrowerlist = borrowerList)
####################
######following functions are for add borrowers
@app.route("/borroweradd", methods=["POST"])
def add_borrower():
    if request.method == "GET":
        return render_template("addborrower.html")
    elif request.method == "POST":
        first_name = request.form.get("firstname")
        family_name = request.form.get("familyname")
        date_of_birth = request.form.get("dateofbirth")
        house_number = request.form.get("housenumbername")
        street = request.form.get("street")
        town = request.form.get("town")
        city = request.form.get("city")
        postal_code = request.form.get("postalcode")

        connection = getCursor()
        connection.execute("INSERT INTO borrowers (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        ( first_name, family_name, date_of_birth, house_number, street, town, city, postal_code))
        connection.commit()

        return redirect(url_for("borrower_list"))


@app.route("/addborrower", methods=["POST"])
def add_borrower_post():

    first_name = request.form.get("firstname")
    family_name = request.form.get("familyname")
    date_of_birth = request.form.get("dateofbirth")
    house_number = request.form.get("housenumbername")
    street = request.form.get("street")
    town = request.form.get("town")
    city = request.form.get("city")
    postal_code = request.form.get("postalcode")

    connection = getCursor()
    connection.execute("INSERT INTO borrowers (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       ( first_name, family_name, date_of_birth, house_number, street, town, city, postal_code))
    connection.commit()

    return redirect(url_for("borrower_list"))

####################display a list of overdue books & their borrowers
@app.route("/overdue")
def overdue():
    connection = getCursor()
    sql=""" SELECT books.booktitle, borrowers.firstname, borrowers.familyname, datediff(curdate(), loandate) as overdue
        FROM ((loans inner join borrowers on loans.borrowerid = borrowers.borrowerid)
            inner join bookcopies on loans.bookcopyid = bookcopies.bookcopyid)
                inner join books on bookcopies.bookid=books.bookid
                    where datediff(curdate(), loandate) > 35; """
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("overdue.html", loanlist = loanList)
###################display a list of Loan Summary

@app.route("/loansummary")
def loansummary():
    connection = getCursor()
    sql = """SELECT  books.bookid, books.booktitle, books.author, books.category, books.yearofpublication,count(bookcopies.bookcopyid) as totalnumber
                FROM bookcopies
                left join loans on bookcopies.bookcopyid = loans.bookcopyid
                left join books on bookcopies.bookid = books.bookid
                group by books.bookid;"""
    connection.execute(sql)
    loanSummary = connection.fetchall()
    return render_template("loansummary.html", loansummary = loanSummary)

#########display a list of borrower summary
@app.route("/borrowersummary")
def borrowersummary():
    connection = getCursor()
    sql = """SELECT borrowers.borrowerid, borrowers.firstname, borrowers.familyname, count(loans.borrowerid) as totalnumber
            FROM borrowers
            LEFT JOIN loans ON borrowers.borrowerid = loans.borrowerid
            GROUP BY borrowers.borrowerid;"""
    connection.execute(sql)
    borrowerSummary = connection.fetchall()
    return render_template("borrowersummary.html", borrowersummary = borrowerSummary)

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