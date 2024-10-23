"""
Banking Transaction Management System

Author(s): Debargha Bose

Overview:
This system manages user bank accounts, allowing users to perform transactions such as deposits and withdrawals. It tracks account balances and maintains a transaction history in a MySQL database.

Requirements:
- Python 3.x
- MySQL Server
- mysql-connector-python (Install with: pip install mysql-connector-python)

Database Setup:
Before running the application, ensure you have a MySQL database set up with the following tables:

1. USERS:
   - ACCOUNT_NUMBER (INT, PRIMARY KEY)
   - BALANCE (FLOAT)

2. widthdral_and_deposit:
   - USER_ACCOUNT_NUMBER (INT, FOREIGN KEY references USERS)
   - WITHDRAWL (FLOAT)
   - DEPOSIT (FLOAT)
   - Date (DATETIME)
   - REMAINING_BALANCE (FLOAT)

Functions:

1. acc_transaction(i)
   - Handles withdrawals and deposits for the specified user account.
   - Parameters:
     - i (int): The account number of the user.
   - Returns: None
   - Functionality:
     - Retrieves the current balance for the account.
     - Prompts the user for withdrawal and deposit amounts.
     - Updates the balance and records the transaction in the database.

2. balance_management()
   - Manages user interactions for balance inquiries and transaction history.
   - Returns: None
   - Functionality:
     - Prompts the user for their account number.
     - Checks if the account exists.
     - Displays transaction history or prompts for new transactions.

Error Handling:
Basic error handling is implemented to manage exceptions during database operations.


Future Improvements:
- Implement user authentication.
- Add transaction summary reports.
- Enhance the user interface.

"""



import mysql.connector as conex


h="localhost"#host maintaing the database
u="root"#username
p="1234"#password
file="confirmation.txt"#file that this program will use to know if it has run once atleast or not

def conx(): ###Will use only the first time the code runs as the other queries in this function[conx()]
            ### are not required to run everytime

    db=conex.connect(host=h,user=u,password=p)#initialization of the connection
    cur=db.cursor()#the cursor
    
    q1="create database if not exists BANK"
    cur.execute(q1)
    cur.execute("USE BANK")

    
    q2="""create table if not exists USERS (
            ACCOUNT_NUMBER INT AUTO_INCREMENT PRIMARY KEY,
            NAME varchar(64) NOT NULL,
            E_MAIL VARCHAR(64) NOT NULL,
            ADDRESS varchar(64) NOT NULL,
            NUMBER BIGINT NOT NULL UNIQUE,
            BALANCE FLOAT NOT NULL,
            DATE_OF_OPENING DATE
        )"""                    ###AUTO_INCREMENT increments or makes new ACCOUNT_NUMBER(s) automatically
    cur.execute(q2)             ### whenever a user gets added in the database

    q3="""create table if not exists FEEDBACK (
            USER_ACCOUNT_NUMBER INT PRIMARY KEY,
            FEEDBACK varchar(255)
        )"""
    cur.execute(q3)
    
    q4="""create table if not exists widthdral_and_deposit (
            USER_ACCOUNT_NUMBER INT,
            WITHDRAWL FLOAT,
            DEPOSIT FLOAT,
            Date_and_time TIMESTAMP,
            REMAINING_BALANCE FLOAT
        )"""
    cur.execute(q4)


    q5="""CREATE table if not exists LOAN (
            USER_ACCOUNT_NUMBER INT PRIMARY KEY,
            APPROVAL VARCHAR(100) DEFAULT "NO",
            LOAN_AMOUNT FLOAT,
            LOAN_BEARER VARCHAR(64),
            INTREST_RATE FLOAT,
            REPAYMENT FLOAT,
            TIME_IN_YEARS INT,
            DATE_OF_CONFIRMATION DATE
        )"""
    cur.execute(q5)

def con1():#will use everytime the code runs for connecting to the database
    db=conex.connect(host=h,user=u,password=p)#initialization of the connection
    cur=db.cursor()#cursor object creation
    cur.execute("USE BANK")
    return db,cur


def db_close(db,cur):
    cur.close()
    db.close()
    return

def acc_existence():#for checking existence of users(no specifics)
    db, cur=con1()
    cur.execute("select ACCOUNT_NUMBER FROM USERS")
    a=cur.fetchall()
    for i in a:
        return (True,i)

def is_nested(tup):
    for item in tup:
        if type(item) == tuple:  # Using `type()`
            return True
    return False


def check_existance(acc):#for checking existence of users(of user accounts)
    db, cur=con1()
    cur.execute("SELECT * FROM USERS WHERE ACCOUNT_NUMBER = %s", (acc,))
    user_data = cur.fetchone()
    
    if user_data is None:
        print("Account number not found.")
        db_close(db, cur)
        return
    else:
        return (True,user_data)

### Admin menu stuff goes here ###


def delete_user():
    db, cur = con1()
    try:
        # Check if account number exists
        cur.execute("SELECT * FROM USERS")
        user_data = cur.fetchone()

        if user_data is None:
            print("There are no records yet...")
            return

        elif user_data:
            print("Account number",user_data[0])
            print("Name:",user_data[1])
            print("E-mail:",user_data[2])
            print("Address:",user_data[3])
            print("Phone number:",user_data[4])
            print("Balance:",user_data[5])
            user_data = cur.fetchone()
            print("These are all the records")
            a=int(input("Enter account number that is to be deleted: "))

            cur.execute("DELETE FROM USERS WHERE ACCOUNT_NUMBER = %s",(a,))
            db.commit()
            print("Account has been deleted")
        else:
            print("something did not work as intended...")
    except Exception as e:
        print(e)

    finally:
        db_close(db, cur)
    
    return#Exit the function


def loan_conf():
    db, cur = con1()
    try:
        cur.execute("SELECT * FROM LOAN where APPROVAL = NO")
        l=tuple(cur.fetchall())#returns tuples inside of a greater list which is
                               # then converted to nested tuple
        if l!=tuple():
            for i in l:
                print(f"""Account number: {i[0]}
Date of loan approval(if any): {i[7]}
Approval: {i[1]}
Loan amount: {i[2]}
Name of loan bearer: {i[3]}
Intrest: {i[4]}
Maximum time required for payment(given by user): {i[6]}
Total Repayment value after {i[6]} years: {i[5]}""",end="\n\n")
        else:
            print("there are no awaitng loan approvals")
            return

        aff=int(input("Enter the account number to approve loan: "))
        cur.execute("SELECT * FROM LOAN WHERE USER_ACCOUNT_NUMBER = %s",(aff,))
        u=cur.fetchone()
        p=float(u[2])
        t=int(u[6])
        annual_rate=float(input("Enter the annual intrest rate: "))*100#percentaging
        n=int(input("Enter the number of payments done over the lifetime of the loan(if any):"))
        intrest=float(p*annual_rate*t)#already percentaged
        annual_pay=p*((intrest/12)/ 1 - (1+(intrest/12))**-n)###formula for finding the repayment value
        qa="UPDATE LOAN SET APPROVAL = %s, INTREST_RATE = %s,REPAYMENT = %s  WHERE USER_ACCOUNT_NUMBER = %s"
        cur.execute(qa, ("YUP!", intrest, annual_pay, aff))
        qb="UPDATE LOAN SET DATE_OF_CONFIRMATION = NOW()"
        cur.execute(qb)
        cur.execute("SELECT * FROM LOAN WHERE USER_ACCOUNT_NUMBER = %s",(aff,))
        u=cur.fetchone()
        print(u,"<-Loan details has been updated")
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db_close(db, cur)


def admin_transaction_viewer():
    
    db,cur=con1()

    cur.execute("SELECT * FROM widthdral_and_deposit")
    r=tuple(cur.fetchall())
    
    if r!=tuple():
        if is_nested(r):
            for i in r:
                print(f"""\n\nAccount number: {i[0]}
Widthdral: {i[1]}
Deposit: {i[2]}
Date of transaction: {i[3]}
Balance Remaining: {i[4]}\n\n""")
        elif not is_nested(r):
            print(f"""\n\nAccount number: {[0]}
Widthdral: {r[1]}
Deposit: {r[2]}
Date of transaction: {r[3]}
Balance Remaining: {r[4]}
Date and time of transactions: {r[5]}\n\n""")

    else:
        print("There are no transactions yet!")
        return
    que=input("Enter y to update transaction and n to not do that...")

    if que=='y':
        try:
            i=input("Enter the account number you want to update balance of: ")
            cur.execute("select BALANCE from USERS where ACCOUNT_NUMBER=%s",(i,))
            
            ba = cur.fetchone()[0]

            z=float(0)

            print(f"Remaining balance is: {ba}")
            
            w=float(input("Enter widthdral ammount: "))
            if w is None:
                w=z
            
            print(f"Widthdral amount: {w}")
            
            d=float(input("Enter deposit amount: "))
            if d is None:
                d=z
            
            print(f"Deposit amount: {d}")
            
            ba=ba-w+d
            
            q="INSERT INTO widthdral_and_deposit (USER_ACCOUNT_NUMBER,WITHDRAWL,DEPOSIT,Date,REMAINING_BALANCE) VALUES(%s,%s,%s,NOW(),%s)"
            cur.execute(q,(i,w,d,ba))
            cur.execute("UPDATE USERS SET BALANCE=%s WHERE ACCOUNT_NUMBER=%s",(ba,i))
            print("changes have been made")
            
            if ba<0:
                print("balance cannot be less than 0")
                ba=ba*(-1)
                cur.execute("UPDATE USERS SET BALANCE=%s WHERE ACCOUNT_NUMBER=%s",(ba,i))
                print("reverted")
                
            elif ba==0:
                print("balance is now equal to 0")
                
        except Exception as e:
            print(e)
        finally:
            db.commit()
            db_close(db,cur)

    else:
        return

def feedback_viewer():
    cur.execute("SELECT * FROM FEEDBACK")
    r=cur.execute
    if is_nested(r):
        for i in r:
            print(i)
    else:
        print(r)

### User Menu stuff goes here ###

def view_acc():
    db,cur=con1()
    acc=int(input("Enter account number to see data: "))
    q6="select * from USERS where ACCOUNT_NUMBER = %s"
    cur.execute(q6, (acc,))
    user_data=cur.fetchone()
    if user_data:
        print("\n\n")
        print(f"""Account number: {user_data[0]}
Name: {user_data[1]}
E-mail: {user_data[2]}
Address: {user_data[3]}
Number: {user_data[4]}
Balance: {user_data[5]}\n\n""")
    else:
        print("User not found.")

    db_close(db, cur)

def add_user():
    db,cur = con1()#unpacking the con1() function
    try:
        n=input("Enter name: ")
        a=input("Enter address: ")
        e=input("Enter E.Mail address(the only valid Email is [gmail.com] for now... ): ")
        pnum=input("Enter phone number: ")
        ball=float(input("Enter balance amount: "))
        validation=e.split()
        v=""
        for i in e:#checking for valid email(Starts)
            if i==" ":
                continue
            else:
                v+=i
        p=v.split('@')
        if p[1]!="gmail.com":#(Ends)
            print("Email not valid error")
        else:
            qa = "INSERT INTO USERS (NAME, ADDRESS, E_MAIL, NUMBER, BALANCE) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(qa, (n, a, v, pnum, ball))
            cur.execute("SELECT LAST_INSERT_ID()")
            rem=cur.fetchone()
            print("your account number is,",rem[0])
            cur.execute("UPDATE USERS SET DATE_OF_OPENING=(NOW())")
            db.commit()
            
    except Exception as e:
        print(e)
    finally:
        db_close(db,cur)


def update_user():
    db, cur = con1()  # unpacking the con1() function
    
    acc = int(input("Enter account number: "))
    n = input("Enter new Name: ")
    e = input("Enter new E.Mail address: ")
    a = input("Enter new address: ")
    pnum = int(input("Enter new phone number: "))
    
    if check_existance(acc) is True:
        try:
            qa = "UPDATE USERS SET NAME=%s, E_MAIL=%s, ADDRESS=%s, NUMBER=%s WHERE ACCOUNT_NUMBER=%s"
            cur.execute(qa, (n, e, a, pnum, acc))
            
            # Commit the changes to the database
            db.commit()
            
            print("User information updated successfully.")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            db_close(db, cur)
    else:
        print("Account not found")
        return


def give_feedback():
    db, cur = con1()
    acc = int(input("Enter your account number: "))
    feedback = input("Enter your feedback: ")
    
    qa = "INSERT INTO FEEDBACK (USER_ACCOUNT_NUMBER, FEEDBACK) VALUES (%s, %s)"
    cur.execute(qa, (acc, feedback))
    print("Feedback submitted successfully.")
    db.commit()
    db_close(db, cur)


def apply_for_loan():
    try:
        db, cur = con1()
        acc = int(input("Enter your account number: "))
        if check_existance(acc):
            loan_amount = float(input("Enter loan amount: "))
            loan_bearer = input("Enter the name of the person who is taking the loan: ")
            t=int(input("Enter time required to pay in years: "))
            qa = "INSERT INTO LOAN (USER_ACCOUNT_NUMBER, LOAN_AMOUNT, LOAN_BEARER, TIME_IN_YEARS) VALUES (%s, %s, %s, %s)"
            cur.execute(qa, (acc, loan_amount, loan_bearer , t))
            print("Loan application submitted successfully.")
            db.commit()

        else:
            print("No accounts found")
    except Exception as e:
        print(e)
    finally:
        db_close(db, cur)


def view_loans():
    db, cur = con1()
    acc = int(input("Enter your account number to view loans: "))
    
    qa = "SELECT * FROM LOAN WHERE USER_ACCOUNT_NUMBER = %s"
    cur.execute(qa, (acc,))
    i= cur.fetchone()#returns tuple
    
    if i:
        print(i,"\n\n\n")
        
        print(f"""Account number: {i[0]}\n
Date of loan approval(if any): {i[7]}\n
Approval: {i[1]}\n
Loan amount: {i[2]}\n
Name of loan bearer: {i[3]}\n
Intrest: {i[4]}\n
Maximum time required for payment(given by user): {i[6]}\n
Total Repayment value after {i[6]} years: {i[5]}\n\n""")
        
    else:
        print("No loans found for this account number.")
    
    db_close(db, cur)

def acc_transaction(i):
    
    db,cur=con1()
    
    cur.execute("select BALANCE from USERS where ACCOUNT_NUMBER=%s",(i,))
    
    ba = cur.fetchone()[0]
    
    print(f"Remaining balance is: {ba}")
    
    w=float(input("Enter widthdral ammount: "))
    
    print(f"Widthdral amount: {w}")
    
    d=float(input("Enter deposit amount: "))
    
    print(f"Deposit amount: {d}")
    
    ba=ba-w+d
    
    q="INSERT INTO widthdral_and_deposit (USER_ACCOUNT_NUMBER,WITHDRAWL,DEPOSIT,Date,REMAINING_BALANCE) VALUES(%s,%s,%s,NOW(),%s)"
    cur.execute(q,(i,w,d,ba))
    cur.execute("UPDATE USERS SET BALANCE=%s WHERE ACCOUNT_NUMBER=%s",(ba,i))
    print("Balance has been updated")
    print("New balance is:",ba)
    
    
    if ba<0:
        print("balance cannot be less than 0 or zero")
        ba=ba*(-1)
        cur.execute("UPDATE USERS SET BALANCE=%s WHERE ACCOUNT_NUMBER=%s",(ba,i))
        print("reverted transaction")
        
    elif ba==0:
        
        print("balance is now equal to zero or 0")
        
    db.commit()
    
    db_close(db,cur)

def balance_management():
    
    db,cur=con1()

    try:
        
        i=int(input("Enter your account number: "))
        
        b=0#initial bool value
        if check_existance(i):
            b=1
            
        if b==1:
            
            cur.execute("select * from widthdral_and_deposit where USER_ACCOUNT_NUMBER=%s",(i,))
            
            p=tuple(cur.fetchall())
            
            if p==tuple():
                
                print("No transaction history found!")
                
                q=input("Do you want to make a new transaction history??(y/n): ").lower()
                if q=='y':
                    acc_transaction(i)
                else:
                    pass
                
            elif p!=tuple():
                if is_nested(p):
                    for r in p:
                        print(f"""\n\nAccount number: {r[0]}
Widthdral: {r[1]}
Deposit: {r[2]}
Date of transaction: {r[3]}
Remaining balance: {r[4]}\n\n""")
                        
                    q=input("Do you want to make a new transaction history??(y/n): ").lower()
                    if q=='y':
                        acc_transaction(i)
                    else:
                        pass
                
                else:#if not nested
                    print(f"""\n\nAccount number: {p[0]}
Widthdral: {p[1]}
Deposit: {p[2]}
Date of transaction: {p[3]}
Remaining balance: {p[4]}\n\n""")

                    q=input("Do you want to make a new transaction history??(y/n): ").lower()
                    if q=='y':
                        acc_transaction(i)
                    else:
                        pass
        else:
            print("There is no known user of that account")
    except Exception as e:
        print(e)
    finally:
        db.commit()
        db_close(db,cur)


### The actual menu part of the User menu ###

def umenu():#User menu
    while True:
        print("*"*57)
        print(r"""
                    //===========\\
                     ||USER MENU||
                    \\===========//

                    """)
        print("*"*57)
        print("""\t\t 1. Add user
                 2. View your bank account data
                 3. Update profile
                 4. Apply for loan 
                 5. Give feedback
                 6. View loan status
                 7. widthdraw or deposit
                 8. Exit""")
        print("Enter the numbers (1,2,3,4,5,6,7,8) to choose...")
        ch=input("Enter choice: ")

        if ch=='1':
            add_user()

        elif ch=='2':#was a simple implimentation so i did it here(and i changed it...)
            view_acc()
        
        elif ch=='3':
            update_user()

        elif ch=='4':
            apply_for_loan()
        
        elif ch=='5':
            give_feedback()

        elif ch=='6':
            view_loans()

        elif ch=='7':
            balance_management()
        
        else:
            print("Exiting...")
            break

### Admin menu ###

def admenu():
    while True:
        print("*"*57)
        print(r"""
                    //============\\
                     ||ADMIN MENU||
                    \\============//
                    """)
        print("*"*57)
        print("""1. Delete user
2. Approve loans
3. Transactions and updations
4. View feedback
e. Exit""")
        ch=input("Enter choice: ")
        if ch=="1":
            delete_user()
        elif ch=="2":
            loan_conf()
        elif ch=="3":
            admin_transaction_viewer()
        elif ch=="4":
            feedback_viewer()
        else:
            print("Exiting...")
            break

### This is the area where the main menu is run ###
def mmenu():
    while True:
        print("Enter 1 for user menu, 2 for admin menu and 3 to exit.")
        ch=input("Enter here: ")
        if ch=='1':
            umenu()
        elif ch=='2':
            print("Default password is 1234")
            pa=input("Enter password: ")
            admin=input("Enter name: ")
            if pa=="1234":
                print(f"Hey, {admin}")
                admenu()
            else:
                print("Invalid credenti@ls!")
        elif ch=='3':
            break


try:#Tries to read from the file named "confirmation.txt" which will help us determine that if the code has
    # been run before or not and thus help us save time...

    with open(file,'r+') as f:
        fr=f.read()
        if fr!="c":
            f.write("c")
            print("Trying to establish connection...")
            conx()#make the database and all the tables it consists
            mmenu()
        elif fr=="c":
            con1()#only connect to the database as this program has run once atleast
            mmenu()

except FileNotFoundError as err:#if the file does not exist this except block code will make the file
    print(f"""File was not found, and the error was {err}...
            Resolving the error""")#and run the main connection function
    with open(file,'w+') as f:
        f.write("c")
        print("Trying to establish connection...(error resolved)")
        conx()
        mmenu()
