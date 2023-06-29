from fastapi import FastAPI
from datetime import datetime
import sqlite3
from sqlite3 import Error
from sqlite3 import Connection
import csv
from fastapi.responses import FileResponse

app = FastAPI()

def create_connection(db_file:str) -> Connection | None:
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_alltasks(conn:Connection,count:int):
    #sql="Select * from ios1"
    sql= f"""
        SELECT * 
        FROM iot1 
        ORDER by date DESC 
        LIMIT {count}
    """
    cursor = conn.cursor()
    cursor.execute(sql)
    rows=cursor.fetchall()
    return rows

def create_table(conn:Connection):
    sql_projects = """
    CREATE TABLE IF NOT EXISTS iot1(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		date TEXT NOT NULL,
		light INTEGER NOT NULL,
		temperature REAL NOT NULL
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql_projects)
    except Error as e:
        print(e)


def insert_project(conn:Connection, project:tuple[str,float,float]):
    sql = """
    INSERT INTO iot1(date,light,temperature)
    VALUES(?,?,?)
    """
    cursor = conn.cursor()
    cursor.execute(sql,project)
    conn.commit()

@app.get("/")
def read_root():
    return {"Hello": "rebort"}

@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"item_id": item_id}


#query parameter
@app.get("/raspberry")
#async def read_items(time:datetime = datetime.now(),light:float = 0.0, temperature:float=0.0):
async def read_items(time:str = datetime.now().strftime("%Y%m%d %H:%M:%S"),light:float = 0.0, temperature:float=0.0):
   #"時間":time.strftime("%Y%m%d %H:%M:%S"),
   conn = create_connection('data.db')
   if conn is not None:
        create_table(conn)
        insert_project(conn, (time,light,temperature))
        conn.close()

   return {
       "時間":time,
       "光線":light,
       "溫度":temperature
   }   

#query parameter
@app.get("/iot_json/{item_count}")
async def read_item2(item_count:int):
    conn = create_connection('data.db')
    if conn is not None:
        create_table(conn)
        rows = select_alltasks(conn,item_count)
        #print(rows)
        conn.close()  
        return rows

#query parameter
@app.get("/iot_csv/{item_count}")
async def read_item3(item_count:int):
    conn = create_connection('data.db')
    if conn is not None:
        create_table(conn)
        rows = select_alltasks(conn,item_count)
        with open('output.csv','w',encoding='utf8',newline='') as file:
            csv_write = csv.writer(file)
            csv_write.writerow(['序','時間','亮度','溫度'])
            for row in rows:
                csv_write.writerow(row)
        #print(rows)
        conn.close()  
        #return rows

    file_path = "output.csv"
    response = FileResponse(file_path, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.csv"
    return response



        