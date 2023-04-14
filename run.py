import subprocess
proc = subprocess.Popen(['python', 'manage.py', 'runserver', '8080'],stdout=subprocess.PIPE)
while True:
  line = proc.stdout.readline()
  if not line:
    break
  #the real code does filtering here
  info = str(line.rstrip().decode("utf-8"))
  print("test:", info)
  if "Quit the server with CTRL-BREAK." == info:
    a = subprocess.Popen(['start', 'electronApp/ru.poisk.exe'],stdout=subprocess.PIPE, shell=True)