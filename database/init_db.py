import sqlite3

conn = sqlite3.connect('report_log.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserName TEXT NOT NULL UNIQUE,
        Password TEXT NOT NULL,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Email TEXT NOT NULL,
        Phone TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Projects (
        ProjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        Address TEXT,
        City TEXT,
        State TEXT,
        ZipCode TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reports (
        ReportID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProjectID INTEGER,
        UserID INTEGER,
        Date DATE NOT NULL,
        Description TEXT NOT NULL,
        HardHatUsed BOOLEAN NOT NULL,
        GlovesUsed BOOLEAN NOT NULL,
        EyeProtectionUsed BOOLEAN NOT NULL,
        EarProtectionUsed BOOLEAN NOT NULL,
        FootwearUsed BOOLEAN NOT NULL,
        DustMaskUsed BOOLEAN NOT NULL,
        OtherPPEUsed TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Workers (
        WorkerID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Role TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProjectWorkers (
        ProjectWorkerID INTEGER PRIMARY KEY AUTOINCREMENT,
        ReportID INTEGER,
        WorkerName TEXT,
        WorkerHours DOUBLE NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Feedback (
        FeedbackID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER,
        Stars INTEGER NOT NULL,
        Comment TEXT,
        Change TEXT,
        Fix TEXT
    )
''')

conn.commit()
conn.close()