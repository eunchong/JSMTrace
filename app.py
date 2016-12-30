#!/usr/bin/env python
from flask import Flask, render_template, session, request, send_from_directory, json, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from JSMTrace.database import JSMT_DB
from run import JSMT_RUNNER
from datetime import datetime
import os

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jsmt_temp_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = ['js']

db = JSMT_DB()
jsmt = JSMT_RUNNER()

socketio = SocketIO(app, async_mode=async_mode)
thread = None


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

eTask      = enum('task_id','js_name','task_state','js_content')
eLineGroup = enum('m_access_type','m_address','m_size','m_id','m_stack_size','m_stack_address','m_stack_is_symbol','line_num','col_num')
eBindTable = enum('line_num','mt_line')


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def to_dict(self):
    return dict([(k, getattr(self, k)) for k in self.__dict__.keys() if not k.startswith("_")])

def bind_log_line(js,line_group_logs):
    jsLineArray = js.split("\n")

    mt_line_dict = {}
    mt_result_js = []
    logBindTable = {}
    lineBindTable= {}

    for mt_info in line_group_logs:
        line_num = mt_info[eLineGroup.line_num]
        if mt_line_dict.has_key(line_num):
            mt_line_dict[line_num].append(mt_info)
        else:
            mt_line_dict[line_num] = [mt_info]

    for idx in range(len(jsLineArray)):
        mt_result_js.append(jsLineArray[idx])

        if mt_line_dict.has_key(idx+1):
            indentSize = len(jsLineArray[idx]) -len(jsLineArray[idx].lstrip())
            for mt_line in mt_line_dict[idx+1]:
                mt_result_js.append("%s// [MTrace] -> %s"%(' '*indentSize,mt_line[:-4]))
                mt_line_no = len(mt_result_js)-1
                if logBindTable.has_key(mt_line[eLineGroup.m_id]):
                    logBindTable[mt_line[eLineGroup.m_id]].append([mt_line_no,mt_line])
                else:
                    logBindTable[mt_line[eLineGroup.m_id]] = [[mt_line_no,mt_line]]
                lineBindTable[mt_line_no] = mt_line[eLineGroup.m_id]
                

    return "\n".join(mt_result_js),logBindTable,lineBindTable

@app.route('/')
def index():
    return render_template('index.html')
    # task = db.get_task_first()
    # line_group_logs = db.get_line_group(task[0]) 
    # logJs, logBindTable, lineBindTable = bind_log_line(task[eTask.js_content],line_group_logs)

@app.route('/<pagename>')
def admin(pagename):
    return render_template(pagename+'.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['js-input']
        if file and allowed_file(file.filename):
            now = datetime.now()

            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'])):
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER']))

            filename = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            file.save(filename)

            jsmt.run([filename,'out.log','sOut.log'])

        else:
            return "<script>alert('upload js only !');location.href='/'</script>";

    return "<script>alert('upload success !');location.href='/'</script>"

@app.route('/task/list', methods=['GET'])
def task_list():
    return json.dumps({'status':'OK','task_list':db.get_task_list()})


@app.route('/task/<int:task_id>', methods=['GET'])
def task(task_id):
    
    task = db.get_task(task_id)
    line_group_logs = db.get_line_group(task_id) 
    logJs, logBindTable, lineBindTable = bind_log_line(task[eTask.js_content],line_group_logs)

    return render_template('blank.html', task=task,logJs=logJs,logBindTable=json.dumps(logBindTable),lineBindTable=json.dumps(lineBindTable))

if __name__ == '__main__':
    socketio.run(app, debug=False,host="0.0.0.0")
