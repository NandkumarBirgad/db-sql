import sqlite3
def db_operation(q):
    con = sqlite3.connect("stude678.db")
    con.execute(q)
    con.commit()
    con.close
def add_new_student():
    sroll = input("Enter Student Roll Number: ")
    sname = input("Enter Student Name:")
    scity = input("enter Student city:")
    q = "insert into student_info values({0}, {1},{2})".format(sroll, sname, scity)
    db_operation(q)
    print("stunde information saved...")
def update_student():
    sroll = input("Enter Student Roll Number: ")
    sname = input("Enter Student Name: ")
    scity = input("enter Student city:")
    q = "update student_info set sname={0}, scity={1}, sroll={2}".format(sname, scity, sroll)
    db_operation(q)
    print("Student information update succsesfully...")
def delete_student():
    sroll = input("Enter Student Roll Number:")
    sname = input("Enter Student Name:")
    scity = input("Enter Student city:")
    q = "delet student_info where sname={0}, scity={1}".format(sname, scity)
    db_operation(q)
    print("Student information delete succsesfully...")
while True:
    print("1. Add New Student")
    print("2 . Update Student")
    print("3. Delete Student")
    print("4. Exit")
    ch = int(input("Enter Your Choice:"))
    if ch ==1:
        add_new_student()
    elif ch ==2:
        update_student()
    elif ch ==3:
        delete_student()
    elif ch ==4:
        exit()

