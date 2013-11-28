import pyping
import sqlite3
import threading
import sys
import rrdtool, tempfile
import time

# sys.path.append('')
conn = sqlite3.connect('ex.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS target
                (t_name text, t_addr text)''')
c.execute('''CREATE TABLE IF NOT EXISTS result
                (r_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, r_name text, r_delay REAL)''')
c.execute("DELETE FROM target")
#c.execute("INSERT INTO target VALUES ('gg', '8.8.8.8')")
#c.execute("INSERT INTO target VALUES ('hh', '168.95.1.1')")
#c.execute("INSERT INTO target VALUES ('err', '192.168.88.1')")
c.execute("INSERT INTO target VALUES ('iperf-b', '172.31.26.112')")
conn.commit()

# for row in c.execute("SELECT t_addr FROM target"):
#     print row

c.execute("SELECT * FROM target")
rows = c.fetchall()
conn.close()

def w_r():
    conn1 = sqlite3.connect('ex.db')
    c1 = conn1.cursor()
    for row in rows:
		t = int(time.time())
		s_t = str(t)
		r = pyping.ping(row[1], count=1)
        #     print row[0] + "=>" + r.avg_rtt
		c1.execute("INSERT INTO result (r_name, r_delay) VALUES (?, ?)", (row[0], r.avg_rtt))
		if r.avg_rtt == None:
			s_delay = '0'
		else:
			s_delay = str(r.avg_rtt)
		data_source = 'DS:delay:GAUGE:2:0:' + s_delay
		rrdtool.create( 'delay.rrd',
						'--start', s_t,
						data_source,
						'RRA:AVERAGE:0.5:1:60')
		conn1.commit()
		SECOND = 60
		MINUTE = 60 * SECOND
		path = '/tmp/delay.png'
		rrdtool.graph(path,
						'--imgformat', 'PNG',
						'--width', '540',
						'--height', '100',
						'--start', s_t,
						'--end', "+1",
						'--vertical-label', 'delay/Day',
						'--title', 'Annual delay',
						'--lower-limit', '0',
						'DEF:response=delay.rrd:delay:AVERAGE',
						'LINE:response#990033')
		info = rrdtool.info('delay.rrd')
		print info['last_update']
		print info['ds[delay].minimal_heartbeat']
    conn1.close()
        
# for row in c.execute("SELECT * FROM result"):
#     print row

def do_every(interval, work_func, iterations = 0):
    if iterations != 1:
        threading.Timer(interval, do_every, [interval, work_func, 0 if iterations == 0 else iterations - 1]).start()
        work_func()

#w_r()
do_every(2, w_r)
