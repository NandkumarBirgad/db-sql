import sqlite3
import datetime

def db_ddl_dml_operations(q):
    con = sqlite3.connect("library_db.db")
    con.execute(q)
    con.commit()
    con.close()

def create_all_tables():

    query1 = """
            create table all_books
            (
              bnum numeric(7),
              btitle varchar(25),
              bauthor varchar(25),
              bpubliation varchar(25)
            )
             """
    query2 = """
            create table all_students
            (
              senr numeric(12),
              sname varchar(25),
              sclass varchar(15),
              semail varchar(40),
              smob numeric(15) 
            ) 
              """
    query3 = """
            create table all_issued
            (
                enr numeric(10),
                bnum numeric(7),
                idate varchar(15),
                rdate varchar(15)
            )
              """
    db_ddl_dml_operations(query1)
    print("Table : all_books created...")
    db_ddl_dml_operations(query2)
    print("Table : all_students created...")
    db_ddl_dml_operations(query3)
    print("Table : all_issued created...")

def get_date():
    a = datetime.date.today()
    sdate = str(a.day) + "-" + str(a.month) + "-" + str(a.year)
    return sdate

def db_select_operations(q):
    pass

def issue_book():
    e = input("Enter Enrollment Number : ")
    b = input("Enter Book Number : ")
    idate = get_date()

    qry = "insert into all_issued values({0}, {1}, '{2}', '{3}' )".format(e,b,idate,"NR")
    db_ddl_dml_operations(qry)
    print("Book Issued...")
    input()

def return_book():
    b = input("Enter Book Number to Return : ")
    ret_date = get_date()

    qry = "update all_issued set rdate={0} " \
          "where bnum={1} and rdate='NR' ".format(ret_date, b)
    db_ddl_dml_operations(qry)
    print("Book Returned..")
    input()

def view_not_ret_books():
    pass

def search_student():
    pass

def search_book():
    pass

def add_new_stud():
    e = input("Enter Enrollment Number : ")
    n= input("Enter Student Name : ")
    cl = input("Enter Class : ")
    em = input("Enter Email : ")
    m = input("Enter Mobile Number : ")

    qry = "insert into all_students values({0}, {1}, {2}, {3}, {4}) ".format(e,n,cl,em,m)
    db_ddl_dml_operations(qry)
    print("New Student Added..")
    input()

def add_new_book():
    pass

def view_stud_history():
    pass

def view_book_history():
    pass

try:
    create_all_tables()
except sqlite3.OperationalError as ex:
    pass

while True:
    print("Select operation")
    print("1 - Issue Book")
    print("2 - Return Book")
    print("3 - View Not Returned Books")
    print("4 - Search Student")
    print("5 - Search Book")
    print("6 - Add New Student")
    print("7 - Add New Book")
    print("8 - View Student History")
    print("9 - View Book History")
    print("0 - Exit")
    ch = int(input("Provide your choice : "))
    if ch==1: issue_book()
    elif ch==2: return_book()
    elif ch==3: view_not_ret_books()
    elif ch==4: search_student()
    elif ch==5: search_book()
    elif ch==6: add_new_stud()
    elif ch==7: add_new_book()
    elif ch==8: view_stud_history()
    elif ch==9: view_book_history()
    elif ch==0: exit(0)