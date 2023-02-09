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

########search for public-->
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

##########public interface list all avaliable book
@app.route("/booklist")
def listbooks():
    connection = getCursor()
    connection.execute("SELECT * FROM books;")
    bookList = connection.fetchall()
    print(bookList)
    return render_template("booklist.html", booklist = bookList)  

######staff interface
@app.route("/staff")
def staff():
    return render_template("staff.html")

######staff search
@app.route("/staff/search", methods=["POST"])
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
    return render_template("staff/search.html", booklist = bookList)

##############this route is display all availability of all copies of a book (staff).

@app.route("/staff_search")
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
    return render_template("staff_search.html", booklist = bookList)

@app.route("/staff_borrowers")
def listborrowers():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("staff_borrowers.html", borrowerlist = borrowerList)

#####following is create a table for search borrowers by name or by id
@app.route("/staff/search_borrower", methods=["POST"])
def searchborrowers():
    searchterm = request.form.get('search')
    searchterm = "%" + searchterm +"%" if searchterm else "%"
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers WHERE borrowers.firstname LIKE %s OR borrowers.familyname LIKE %s OR borrowers.borrowerid LIKE %s;",(searchterm, searchterm, searchterm,))
    borrowerList = connection.fetchall()
    return render_template("staff/search_borrower.html", borrowerlist = borrowerList)

#############  update borrowers ##########
@app.route("/update_borrower")
def up1():
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    return render_template("update_borrower.html", borrowers= borrowerList)

@app.route("/staff/update_borrower", methods=["POST"])
def up2():     
    borrowerid = request.form.get('borrower')
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers where borrowers.borrowerid = %s",(borrowerid,))
    borrowerList = connection.fetchall()   
    return render_template("staff/update_borrower.html", borrowers= borrowerList)
    
@app.route("/staff/update_borrower_submit", methods=["POST"])
def up3():   
        borrowerid = request.form.get('borrowerid')
        firstname = request.form.get('firstname')
        familyname = request.form.get('familyname')
        dateofbirth = request.form.get('dateofbirth')
        housenumbername = request.form.get('housenumbername')
        street = request.form.get('street')
        town = request.form.get('town')
        city = request.form.get('city')
        postalcode = request.form.get('postalcode')
        connection = getCursor()
        connection.execute("UPDATE borrowers SET firstname = %s, familyname= %s, dateofbirth = %s, housenumbername = %s, street = %s, town = %s, city = %s, postalcode= %s  \
            WHERE borrowerid = %s ",(firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode, borrowerid,))  
        connection.execute("SELECT * FROM borrowers where borrowers.borrowerid = %s",(borrowerid,))
        borrowerList = connection.fetchall()      
        return render_template("staff_borrowers.html",borrowerlist= borrowerList)

######add new borrower
@app.route("/add_borrower", methods=["GET", "POST"])
def add_borrower():
    if request.method == "GET":
        return render_template("add_borrower.html")
    else:
        first_name = request.form.get("first_name")
        family_name = request.form.get("family_name")
        date_of_birth = request.form.get("date_of_birth")
        house_number = request.form.get("house_number")
        street = request.form.get("street")
        town = request.form.get("town")
        city = request.form.get("city")
        postal_code = request.form.get("postalcode")

        connection = getCursor()
        connection.execute("INSERT INTO borrowers (firstname, familyname, dateofbirth, housenumbername, street, town, city, postalcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        ( first_name, family_name, date_of_birth, house_number, street, town, city, postal_code))    
    return redirect(url_for("listborrowers"))

#########issue book
@app.route("/issue_book")
def loanbook():
    todaydate = datetime.now().date()
    connection = getCursor()
    connection.execute("SELECT * FROM borrowers;")
    borrowerList = connection.fetchall()
    sql = """SELECT * FROM bookcopies
inner join books on books.bookid = bookcopies.bookid
where bookcopyid not in(select distinct loans.bookcopyid from loans inner join bookcopies on bookcopies.bookcopyid = loans.bookcopyid
where (bookcopies.format not in('eBook', 'Audio Book')and loans.returned<>1 or loans.returned is null));"""
    connection.execute(sql)
    bookList = connection.fetchall()
    return render_template("issue_book.html", loandate = todaydate,borrowers = borrowerList, books= bookList)
@app.route("/loan/add", methods=["POST"])
def addloan():
    borrowerid = request.form.get('borrower')
    bookid = request.form.get('book')
    loandate = request.form.get('loandate')
    cur = getCursor()
    cur.execute("INSERT INTO loans (borrowerid, bookcopyid, loandate, returned) VALUES(%s,%s,%s,0);",(borrowerid, bookid, str(loandate),))
    return redirect("/currentloans")
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
                            where l.returned = 0
            order by br.familyname, br.firstname, l.loandate DESC;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("currentloans.html", loanlist = loanList)

#######return a book
@app.route("/returnbook")
def returnbook():

    connection = getCursor()
    sql = "SELECT * FROM loans WHERE returned = 0;"
    connection.execute(sql)  
    loanList = connection.fetchall()
    return render_template("returnloan.html", loans = loanList)
@app.route("/loan/return", methods=["POST"])
def returnloan():
    loanid = request.form.get('loan')  
    cur = getCursor()
    cur.execute("update loans set loans.returned = '1' where loanid = %s", (loanid,))

        
    return redirect("/currentreturn")
@app.route("/currentreturn")
def currentreturn():
    connection = getCursor()
    sql=""" select br.borrowerid, br.firstname, br.familyname,  
                l.borrowerid, l.bookcopyid, l.loandate, l.returned, b.bookid, b.booktitle, b.author, 
                b.category, b.yearofpublication, bc.format 
            from books b
                inner join bookcopies bc on b.bookid = bc.bookid
                    inner join loans l on bc.bookcopyid = l.bookcopyid
                        inner join borrowers br on l.borrowerid = br.borrowerid
                            where l.returned = 1
            order by br.familyname, br.firstname, l.loandate DESC;"""
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("currentreturn.html", loanlist = loanList)

####################display a list of overdue books & their borrowers
@app.route("/overdue")
def overdue():
    connection = getCursor()
    sql=""" SELECT books.booktitle, borrowers.firstname, borrowers.familyname, datediff(curdate(), loandate) as overdue
        FROM ((loans inner join borrowers on loans.borrowerid = borrowers.borrowerid)
            inner join bookcopies on loans.bookcopyid = bookcopies.bookcopyid)
                inner join books on bookcopies.bookid=books.bookid
                    where loans.returned = 0 and datediff(curdate(), loandate) > 35; """
    connection.execute(sql)
    loanList = connection.fetchall()
    return render_template("overdue.html", loanlist = loanList)

###################display a list of Loan Summary
@app.route("/loan_summary")
def loansummary():
    connection = getCursor()
    sql = """SELECT  books.bookid, books.booktitle, books.author, books.category, books.yearofpublication,count(loans.loanid) as totalnumber
                FROM loans
                inner join bookcopies on loans.bookcopyid = bookcopies.bookcopyid
                inner join books on bookcopies.bookid = books.bookid
                group by books.bookid;"""
    connection.execute(sql)
    loanSummary = connection.fetchall()
    return render_template("loan_summary.html", loansummary = loanSummary)

#########display a list of borrower summary
@app.route("/borrowersummary")
def borrowersummary():
    connection = getCursor()
    sql = """SELECT borrowers.borrowerid, borrowers.firstname, borrowers.familyname, count(loans.loanid) as totalnumber
            FROM loans
            INNER JOIN borrowers ON loans.borrowerid = borrowers.borrowerid
            GROUP BY borrowers.borrowerid;"""
    connection.execute(sql)
    borrowerSummary = connection.fetchall()
    return render_template("borrowersummary.html", borrowersummary = borrowerSummary)



