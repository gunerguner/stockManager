import os,datetime

current_dir = os.path.abspath(os.path.dirname(__file__))
backup_target = current_dir+'/'+str(datetime.date.today())+'.sqlite3'

target_file = os.path.abspath(os.path.join(os.getcwd(), "../db.sqlite3"))

os.system('cp '+target_file+' '+backup_target)