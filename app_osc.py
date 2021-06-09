import os
from util.database import Databese
from util.alarms import OscAlarm, Alarm
from util.query import get_resultes
from util.email.template import Template
from util.email.send_email import Sender
from dotenv import load_dotenv
import logging
from pathlib import Path
from util.base_function import (
                        check_is_reported,
                        log_alarm,
                        validate_osc_in_mut,
                        validate_rem_dupli_wdm
)


###############CONFIG########################
BASE_DIR=Path(__file__).resolve().parent
LOG_DIR = (BASE_DIR / "log")
os.makedirs(LOG_DIR, exist_ok=True)

EMAIL_RECIPIENTS = [ "**@orange.com", "**@orange.com" ] 

load_dotenv()
db = os.environ.get("DATABASE")
host_db = os.environ.get("HOST_DB")
user_db = os.environ.get("USER_DB")
pass_db = os.environ.get("PASSWORD_DB")
#######################################

logging.basicConfig(format = '%(asctime)s   %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO, filename = (LOG_DIR / 'app_osc.log'))

logging.info(f"***Start APP_OSC.***")

db_init = False
debugFlag = True

# debugFlag = False
def debug(x):
    if debugFlag: print(x)


# get results
qr_result_osc_los = get_resultes()
qr_result_mut_los = get_resultes(alarm_query ="MUT_LOS")

# # create obj
if qr_result_osc_los and qr_result_mut_los:
    Databese.initialise(database = db, host = host_db, user = user_db, password = pass_db)
    db_init = True
    osc_alarm_obj = [ OscAlarm(item) for item in qr_result_osc_los]
    mut_alarm_obj = [ Alarm(item) for item in qr_result_mut_los]
else:
    osc_alarm_obj = None
    mut_alarm_obj = None

#validation
if osc_alarm_obj and mut_alarm_obj:
    list_valid_obj = validate_osc_in_mut(osc_alarm_obj, mut_alarm_obj)
    print(f"OSC LOS with MUT LOS alarms nr: {len(list_valid_obj)}")
    logging.info(f"OSC LOS with MUT LOS alarms nr: {len(list_valid_obj)}")
    if list_valid_obj:
        obj_lst_to_render= validate_rem_dupli_wdm(list_valid_obj) 
        print(f"After removing duplicate sections: {len(obj_lst_to_render)}")
        logging.info(f"After removing duplicate sections: {len(obj_lst_to_render)}")
        obj_lst_to_render = [obj for obj in obj_lst_to_render if not check_is_reported(obj)]  
        obj_lst_to_render = [obj for obj in obj_lst_to_render if not check_is_reported_by_alm_id(obj)]  
        print(f"After removing reported alarms, to the report: {len(obj_lst_to_render)}")
        logging.info(f"After removing reported alarms, to the report: {len(obj_lst_to_render)}")
    else:
        obj_lst_to_render = None
else:
    obj_lst_to_render = None


list_msg = []
if obj_lst_to_render:
    for i in obj_lst_to_render:
        log_alarm(i)
        list_msg.append(i.render())
        logging.info(f"Send: {i.render()}")

for i in list_msg:
    Sender( subject="OSP: OSC LOS alarm", template_file= "email_osc.txt", template_file_html = "email_osc.html", context = i,  to_emails = EMAIL_RECIPIENTS).send()
	
#     msg = Sender( subject="Test OSC LOS", template_file= "email_osc.txt",  context = i).format_msg()
#     print(msg)
# 
# for i in obj_lst_to_render:
#     print("************")
#     print(i.port_loca)
    # print(i.ne_name)
    # print(i.alarm_object)
    # print('#')
    # print(i.alarm_source_name())
    # print(i.set_port_name())
    # print(i.get_port_attribute(i.set_port_name()))
    # print('#')
    # print(i.port_osc_oa())
    # print(i.oa_port_name1())
    # print(i.oa_port_name2())
    # print(i.wdm_section_name())
    # print(i.section_wdm)
    # print(i.find_OT(i.section_wdm))
    # print(i.find_GIS())
    # print(i.timestamp)

if db_init:
    Databese.close_all_connection()

logging.info(f"***End APP_OSC.***")
