# 636-webapp
COMP636-S1-2023-Web App

Web Application Project Report


Introduction

This report provides an overview of the solution for the web-based library management system for Waikirikiri Library. This system has both a public interface and a staff interface with a MySQL database using the python connector library to perform various operations to manage books, borrowers and loans.

Solution Structure

The solution consists of several routes and functions that work together to provide a friendly user experience.
There are two main templates, “/” and”/staff”.

Public interface:

/: the home page of the public interface will display when the default route is accessed “/”, also, it’s the base for”/search” and “/booklist”.

/search: this route is accessible via a post request and searches for books based on the search term entered by the user in the “/” (public.html) template. The function “searchbooks ()” of this route is to select the availability of all copies of a book if the copy on loan shows the due date (the loan period is 28 days).

/booklist: this route is list all the books in the database and displays the result in the “booklist.html” template.

Staff interface:

/staff: the home page of the staff interface, can be accessed without logging in. There is no link to the staff interface from the public interface. Also, the “staff.html” is the base for all other templates except the three public templates that have been shown above.

/staff_serach: displaying all the available copies of a book. The results are displayed in the “staff_search.html” template, and the submit button on this page link to the “/staff/search” route. The function name is "staffbc ()”.

/staff/search: this route is accessible via a post request and searches for books based on the search term entered by the user in the “staff_search.html” template. The results are displayed in the” /staff/search.html” template. Function name “staffsearch”. These two functions “staffbc()" and "staffsearch()" have the same SQL query as "searchbooks()”. But return to different pages. The query to retrieve books whose title or author matches the search term. Then pass the resulting to the page and renders it. 

/Staff_borrowers: this route performs a SQL query on the borrowers table to retrieve all borrowers, passes the resulting borrower list to the staff_borrowers.html template and renders it.

/staff/search_borrower: this route is a POST request that takes a search term from a form on the staff_borrowers.html page and performs a SQL query on the borrowers table to retrieve borrowers whose name or ID match the search term. Then passes the resulting borrower list to the staff/search_borrowers.html and renders it.

/update_borrower: this route performs a SQL query the same as"/staff_borrower", passes the resulting list to the update_borrowers.html page and renders it. This page shows a drop box of all borrowers’ ID and name the submit button on update_borrower use the access to /staff/update_borrower via a POST request and shows the selected borrowers’ information on the staff/update_borrower.html template.

/staff/update_borrower: this route is a POST request as I mentioned in the /update_borrower, the submit button on this page links to the /staff/update_borrower_submit" template via POST request. This will get all the information users enter in the input box and use the first SQL update query to update the details of the selected borrower. Then execute the second SQL query to display the new information of the borrower table to staff_borrowers.html.

/add_borrower: this route has both POST and GET methods when the method is GET, it’ll return to “add_borrower.html” showing first name, family name, date of birth, and other details that need to be added with the input box. the submit will request POST and insert the above information to borrowers table, then return to the function “listborrowers”, which is the route /staff_borrowers I listed previously.

/issue_book: this route request two queries for borrowers and available books (returned not 1 in table loans) separately, and shows the result on issue_book.html as two drop box. the submit button links to the next route /loan/add with POST method.

/loan/add: this route with a POST method, which gets borrowerid, bookid, loandate inserted into table loans, and redirects to currentloans.html templates.

/currentloans: this route performs a SQL query inner join four tables to show all the current loan books as a table to the currentloans.html template.

/returnbook: This endpoint generates a list of all the loans that have not been returned and displays it on the returnloan.html template.

/loan/return: this route processes a POST request and updates the returned status of the book when the form is submitted. After the update, the user is redirected to the /currentreturn endpoint.

/currentreturn: this route generates a list of all returned books and displays on the currentreturn.html template with borrower's and books' information.

/overdue: this endpoint generates a list of all overdue books, which means the book has been on loan longer than 35 days. The result table group all overdue books by the borrower and display them on the overdue.html template.

/loan_summary: this route generates a summary of the number of times each book has been loaned. Then return the result to loan_summary.html.

/borrowersummary: this route execute a SQL query to show a table of all borrowers and the number of loans in total they each have had. Then showing the result on borrowersummary.html page.

Assumptions and Design Decisions

The user interface was designed to be easy to navigate and use. The main navigation menu is located at the top of the page, and the theme colours are simple grey and blue. The application uses two separate templates for public and staff interfaces. The “/” (public.html) is the base for”/search” and “/booklist”, and the “/staff” (staff.html) is the base for all other templates except three public interface templates.

The reason for having two separate templates, public.html and staff.html, is to create a clear distinction between the pages for public use and staff use. If two interfaces share a page template, it's easy for them to jump out of each other. Then, using two templates is an easy way for users to navigate and find the information they need. Besides, the staff template is separate from the public page to ensure that staff members have access to all the necessary features to ensure their good productivity. Finally, the requirements state that neither interface requires a login. Therefore, having a separate template is the best option.

The application detects the method used to make a request GST or POST to determine which page to display.
For example, the “returnloan” function uses the POST method:

@app.route("/loan/return", methods=["POST"])
def returnloan():
    loanid = request.form.get('loanid')
    bookcopyid = request.form.get('bookcopyid')  
    borrowerid= request.form.get('borrowerid')  
    loandate = request.form.get('loandate')   
    cur = getCursor()
    cur.execute("update loans set loans.returned = '1' where loanid = %s", (loanid,))
    return redirect("/currentreturn")
 
The reason for this is that the "returnloan" function is used to process the data sent from a form. The form sends data to the server in the body of the request, and the POST method is used for this.
Sometimes the function can handle request methods both GET and POST.
For instance, the “add_borrower” function is used to handle requests to the “/add_borrower" endpoint and accepts both GET and POST methods. 

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

The function first checks the request method, if the method is GET, the function returns the add_borrower.html template, which means that the user is requesting to view the form for adding a borrower. Then if the method is POST, the function retrieves the data from the form submitted by the user using “request.form.get()” get data to execute the query insert the data into the borrowers table, and finally, redirect to the page staff_borrowers.html (function: listborrowers). 

Changes for Multiple Library Branches

If this application was to support multiple library branches, the following changes would be required:

Changes of Database

New tables and modifications to existing tables could be required. The table would have other relevant information, the primary key for this table would be a unique identifier for each branch, and the existing tables such as books and borrowers will need to have a foreign key column added that links to the new library branch table. For example, the format in bookcopies table could be a foreign key link to the loans table to create physical books that can only be loaned once at a time, and other books can be loaned multiple times simultaneously. 

Changes in Design and Implementation

The user interface will require updating. Users can interact with different interfaces after logging in as they have different permissions. The “issue book” and "return book" will be changed as the drop-down menu could not handle a mass of data and multiple library branches. More functions will be added, and the navigation interface needs to be redesigned, using a more concise design, hiding part of the feature under part of the function, which operates effectively to match users’ different needs. More user input needs to be validated to ensure that the correct branch is entered.

Conclusion

The web application project for Waikiribiri Library has successfully provided a solution for the library management system with a public and staff interface. The solution is structured with multiple routes and functions, the endpoints are accessible via GET and POST methods, and borrowers and staff have separate templates base. For future use with multiple library branches, both the database and design need to be changed for more efficiency and better user experience.
