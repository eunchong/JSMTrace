from sqlalchemy import (create_engine, MetaData, Column, Integer, String,
        Unicode, Numeric, func, literal, select,DateTime,TIMESTAMP,BIGINT,Enum,BLOB,JSON,ForeignKey,Index,distinct )
from sqlalchemy.orm import sessionmaker, column_property,relationship,backref,relation,aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy import asc

from config import Config
import argparse
import json
import datetime
import hashlib

#####init DataBase#####
f = file('settings.cfg')
cfg = Config(f)

# engine = create_engine('mysql://%s:%s@%s/%s?charset=utf8'%(cfg.DATABASE_ID,cfg.DATABASE_PASSWORD,cfg.DATABASE_HOST,cfg.DATABASE_NAME), echo=False)
engine = create_engine('sqlite:///test.db', convert_unicode=True,echo=False)
metadata = MetaData(engine)
session = sessionmaker(bind=engine)()
Base = declarative_base(metadata=metadata)

class JSMTraceTask(Base):
    __tablename__ = 'jsmt_task'

    task_id = Column(Integer, autoincrement=True, primary_key=True)
    task_state = Column(Enum("init", "running", "success", "fail", "timeout", name='task_state_enum'), nullable=False)

    js_name = Column(String(38),index=True)
    js_content = Column(BLOB)
    js_content_hash = Column(String(38), index=True)
    js_detail = Column(BLOB)

    t_log = relationship("JSMTraceTLog", backref=backref('jsmt_task'))

    created_time = Column(DateTime, default=datetime.datetime.utcnow)
    last_reqtime = Column(DateTime, default=datetime.datetime.utcnow)


class JSMTraceTLog(Base):
    __tablename__ = 'jsmt_tlog'

    log_id = Column(Integer, autoincrement=True, primary_key=True)
    task_id = Column(Integer, ForeignKey('jsmt_task.task_id'))

    line_num = Column(Integer)
    col_num = Column(Integer)

    m_id = Column(Integer)
    m_context_id = Column(Integer)
    m_size = Column(Integer)
    m_address = Column(Integer)
    m_access_type = Column(Enum("alloc", "free", "load", "store", name='access_type_enum'), nullable=False)

    m_stack_size = Column(Integer)
    m_stack_address = Column(Integer)
    # m_stack_is_symbol = Column(Integer)

    __table_args__ = (Index('log_mid', "log_id", "m_id"), 
        Index('log_mcid', "log_id", "m_context_id"),
        Index('log_msize', "log_id", "m_size"),
        Index('log_maddress', "log_id", "m_address"),
        Index('log_mtype', "log_id", "m_access_type"),)


class JSMT_DB(object):

    def __init__(self):
        pass

    def db_reset(self):
        if raw_input('database will be cleaned. OK? [Y/n]') in {'n', 'N'}:
            metadata.drop_all()
            metadata.create_all()

    def db_create(self):
        metadata.create_all()

    def add_task(self,js_name,js_content):
        m = hashlib.md5()        
        m.update(js_content)
        hashdata = m.hexdigest()

        task = JSMTraceTask(js_name=js_name,js_content=js_content,js_content_hash=hashdata,task_state="init")
        session.add(task)

        try:
            session.commit()
        except:
            session.rollback()
            print "[+] JSMTrace Database Exception : add task fail."
            return False

        return task.task_id

    def set_task_state(self,task_id,task_state):
        task = session.query(JSMTraceTask).filter(JSMTraceTask.task_id == task_id).update({"task_state": task_state})

        try:
            session.commit()
        except:
            session.rollback()
            print "[+] JSMTrace Database Exception : set task state fail."
            return False

        return task


    def add_log(self,task_id,line_num,col_num,m_id,m_context_id,m_size,m_address,m_access_type,m_stack_size,m_stack_address):
        tlog = JSMTraceTLog(task_id=task_id,line_num=line_num,col_num=col_num,m_id=m_id,m_context_id=m_context_id,m_size=m_size,m_address=m_address,m_access_type=m_access_type,m_stack_size=m_stack_size,m_stack_address=m_stack_address)
        session.add(tlog)

        try:
            session.commit()
        except:
            session.rollback()
            print "[+] Exception : add log fail."
            return False

        return tlog.log_id

    def get_group_by_mid(self,task_id):
        t = session.query(JSMTraceTLog.m_id).filter(JSMTraceTLog.task_id==task_id).group_by(JSMTraceTLog.m_id).having(func.count(distinct(JSMTraceTLog.m_context_id))>1).subquery('t')
        result = session.query(JSMTraceTLog.m_access_type,JSMTraceTLog.m_address,JSMTraceTLog.m_size,JSMTraceTLog.m_id,JSMTraceTLog.m_stack_size,JSMTraceTLog.m_stack_address,literal(''),JSMTraceTLog.line_num.concat('#').concat(JSMTraceTLog.col_num)).filter(and_(JSMTraceTLog.task_id==task_id, JSMTraceTLog.m_id==t.c.m_id)).order_by(JSMTraceTLog.m_id).all()
        return result

    def get_group_by_line(self,task_id):
        t = session.query(JSMTraceTLog.m_id).filter(JSMTraceTLog.task_id==task_id).group_by(JSMTraceTLog.m_id).having(func.count(distinct(JSMTraceTLog.m_context_id))>1).subquery('t')
        result = session.query(JSMTraceTLog.m_access_type,JSMTraceTLog.m_address,JSMTraceTLog.m_size,JSMTraceTLog.m_id,JSMTraceTLog.m_stack_size,JSMTraceTLog.m_stack_address,literal(''),JSMTraceTLog.line_num.concat('#').concat(JSMTraceTLog.col_num)).filter(and_(JSMTraceTLog.task_id==task_id, JSMTraceTLog.m_id==t.c.m_id)).filter(and_(JSMTraceTLog.task_id==task_id, JSMTraceTLog.m_id==t.c.m_id)).order_by(JSMTraceTLog.line_num,JSMTraceTLog.col_num).all()
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reset", help="Reset DB", action='store_true')
    parser.add_argument("-c", "--create", help="Creat DB", action='store_true')
    parser.set_defaults(RESET=False)
    args = parser.parse_args()

    if args.reset:
        db = JSMT_DB()
        db.db_reset()
        print "Database Clear !"

    if args.create:
        db = JSMT_DB()
        db.db_create()
        print "Database Create !"

if __name__ == '__main__':
    main()
