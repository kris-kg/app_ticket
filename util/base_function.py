import os
import re
from datetime import datetime
from .database import CursorFromConnectionFromPool


# db queries
query_rec_alm = 'INSERT INTO "tickets_alarm" ("time_reported", "ticket_app", "ticket_id", "reported_to_tt", "es_alarm_id", "probableCause", "timestamp_NFM", \
"event_start_time", "ne_name", "ne_port", "link", "ot", "remarks", "alarm_detail") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
query_check_alm = 'SELECT "es_alarm_id" FROM "tickets_alarm" WHERE "es_alarm_id" = %s'
query_check_alm_detail = 'SELECT "alarm_detail" FROM "tickets_alarm" WHERE "alarm_detail" = %s'
query_source_port = 'SELECT * FROM tx_wdm_hua_cable WHERE "Source_NE" =%s AND "Source_Port" LIKE %s'
query_sink_port = 'SELECT * FROM tx_wdm_hua_cable WHERE "Sink_NE" =%s AND "Sink_Port" LIKE %s'
query_ot = """SELECT id_trail, id_trail_proteccion, nodo_a, nodo_z, n_serie, señal FROM giros_trails_extendidos_light WHERE \
            "nodo_a" =%s AND "nodo_z" =%s AND "n_serie" =%s AND "señal" = 'WDM'"""
query_gis = 'SELECT "SERVICE", "TRAIL", "FROM_EQUIPMENT_NAME", "FROM_HUB", "TO_EQUIPMENT_NAME", "TO_HUB" FROM "GIS_NE_exp04_route" WHERE "TRAIL" LIKE  %s'      
ot = "https://giros.orange.es/Giros/giros.MenuNavegacion/previsualizarOT?id="

datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def switch_ends_wdm(wdm_name):
    try:
        temp_name_list = wdm_name.split("_")
        new_name = f"{temp_name_list[1]}_{temp_name_list[0]}_{temp_name_list[2]}_{temp_name_list[3]}"
    except:
        new_name = None
    return new_name


#dane = self.get_port_attribute(self.port_name) --> returns dict 
def get_fiber_date(dane, q = query_source_port):
    with CursorFromConnectionFromPool() as cr:
        if q == query_source_port:
            cr.execute(q, ( dane['ne'], f"%{dane['shelf']}%{dane['slot']}%{dane['card']}%-{dane['port']}%" ))
            result = cr.fetchall()
        if q == query_sink_port:
            cr.execute(q, ( dane['ne'], f"%{dane['shelf']}%{dane['slot']}%{dane['card']}%-{dane['port']}%" )) 
            result = cr.fetchall()  
        if result:
            # print(f"Result get_fiber_date {result}")
            port_info = {"Name": result[0][0],
                            "Source_NE": result[0][3],
                            "Source_Port": result[0][4],
                            "Sink_NE": result[0][5],
                            "Sink_Port": result[0][6]
                            }
            return port_info


# find ot base on section name/link
def find_OT(section_name): 
    if section_name:
        temp_section = section_name.split("_")
        if len(temp_section) > 3:
            with CursorFromConnectionFromPool() as cr:
                cr.execute(query_ot,( temp_section[0], temp_section[1], temp_section[3]))
                row_result = cr.fetchall()
                if row_result:
                    return row_result[0][0]
                else:
                    with CursorFromConnectionFromPool() as cr:
                        cr.execute(query_ot,( temp_section[1], temp_section[0], temp_section[3]))
                        row_result = cr.fetchall()
                        if row_result:
                            return row_result[0][0]


def find_GIS(section_wdm): 
    if section_wdm:
        temp_section = "_".join(section_wdm.split('_',4)[:4])
        with CursorFromConnectionFromPool() as cr:
            cr.execute(query_gis,( f"%{temp_section}%",))
            row_result = cr.fetchone()
            if row_result:
                return f"Trail: {row_result[1]}, Service: {row_result[0]}, From Equipment: {row_result[2]}, From Hub: {row_result[3]}, To Equipment: {row_result[4]}, To Hub: {row_result[5]}"
            else:
                switch_temp_section = self.switch_ends_wdm(temp_section)
                if switch_temp_section:
                    with CursorFromConnectionFromPool() as cr:
                        cr.execute(query_gis,( f"%{switch_temp_section}%",))
                        row_result = cr.fetchone()
                        if row_result:
                            return f"Trail: {row_result[1]}, Service: {row_result[0]}, From Equipment: {row_result[2]}, From Hub: {row_result[3]}, To Equipment: {row_result[4]}, To Hub: {row_result[5]}"


# check if alarm id exist in db(if repored)
def check_is_reported(id):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_check_alm, (id,))
        rows = cr.fetchone()
        if rows:
            return True

def check_is_reported_by_alm_id(id):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_check_alm_detail, (id,))
        rows = cr.fetchone()
        if rows:
            return True

# check if alarm id exist in db(if repored) base on obj
def check_is_reported(obj):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_check_alm, (obj.alarm_id,))
        rows = cr.fetchone()
        if rows:
            return True
  
def check_is_reported_by_alm_id(obj):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_check_alm_detail, (obj.alarm_detail,))
        rows = cr.fetchone()
        if rows:
            return True

# save reported alalrm to db base on list 
def log_alarm_list(list):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_rec_alm, (*list))


# save reported alalrm to db base on obj
def log_alarm(obj):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(query_rec_alm, (
                                        datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                                        "app_osc",
                                        "NULL",
                                        "ND",
                                        obj.alarm_id,
                                        "OSC LOS",
                                        obj.timestamp,
                                        obj.event_start_time,
                                        obj.ne_name,
                                        obj.port_loca,
                                        obj.wdm_section_name(),
                                        find_OT(obj.wdm_section_name()),
                                        "NULL",
                                        obj.alarm_detail.split('_')[-2]
                                    ))


# remove osc if not mut obj list, base on shelf
def validate_osc_in_mut(obj_lst_osc, obj_lst_mut):
    pattern = re.compile(r"(.+-Shelf\d+)")
    osc_list = []
    for item_osc in obj_lst_osc:
        osc_shelf = item_osc.set_port_name()
        for item_mut in obj_lst_mut:
            mut_shelf = item_mut.set_port_name()
            if (re.findall(pattern, osc_shelf)) == (re.findall(pattern, mut_shelf)):
                osc_list.append(item_osc)
    final_list = set(osc_list)
    return list(final_list)      


# remove redundant and none wdm section
def validate_rem_dupli_wdm(alarm_obj):
    validate_alarm_obj = []
    wdm_list = []
    for item in alarm_obj:
        wdm =item.wdm_section_name()
        if wdm != None and wdm not in wdm_list:
            wdm_list.append(wdm)
            validate_alarm_obj.append(item)
        else:
            pass
    return validate_alarm_obj
