import os
import re
from datetime import datetime
from .database_hendler import query, getresult, execquery


datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def switch_ends_wdm(wdm_name):
    try:
        temp_name_list = wdm_name.split("_")
        new_name = f"{temp_name_list[1]}_{temp_name_list[0]}_{temp_name_list[2]}_{temp_name_list[3]}"
    except:
        new_name = None
    return new_name


def get_fiber_date(dane, q='source'):
    """
    qury table tx_wdm_hua_cable base on the dict builded from func get_port_attribute(port)
    """
    if q == 'source':
        result = getresult(query['source_port'], ( dane['ne'], f"%{dane['shelf']}%{dane['slot']}%{dane['card']}%-{dane['port']}%" ))
    if q == 'sink':
        result = getresult(query['sink_port'], ( dane['ne'], f"%{dane['shelf']}%{dane['slot']}%{dane['card']}%-{dane['port']}%" ))
    if result:
        port_info = {"Name": result[0],
                    "Source_NE": result[3],
                    "Source_Port": result[4],
                    "Sink_NE": result[5],
                    "Sink_Port": result[6]
                    }
        return port_info


def find_OT(section_name):
    """
    find ot base on section name
    """
    if section_name:
        temp_section = section_name.split("_")
        if len(temp_section) > 3:
            rows_result = getresult(query['ot'], ( temp_section[0], temp_section[1], temp_section[3]), allrows = True)
            if rows_result:
                return rows_result[0][0]
            else:
                rows_result = getresult(query['ot'], ( temp_section[1], temp_section[0], temp_section[3]), allrows = True)
                if rows_result:
                    return rows_result[0][0]


def find_GIS(section_wdm): 
    if section_wdm:
        temp_section = "_".join(section_wdm.split('_',4)[:4])
        row_result = getresult(query['gis'], ( f"%{temp_section}%",))
        if row_result:
            return f"Trail: {row_result[1]}, Service: {row_result[0]}, From Equipment: {row_result[2]}, From Hub: {row_result[3]}, To Equipment: {row_result[4]}, To Hub: {row_result[5]}"
        else:
            switch_temp_section = self.switch_ends_wdm(temp_section)
            if switch_temp_section:
                row_result = getresult(query['gis'], ( f"%{switch_temp_section}%",))
                if row_result:
                    return f"Trail: {row_result[1]}, Service: {row_result[0]}, From Equipment: {row_result[2]}, From Hub: {row_result[3]}, To Equipment: {row_result[4]}, To Hub: {row_result[5]}"



# check if alarm id exist in db(if repored)

def check_is_reported(id):
    #for obj use in arg (obj.alarm_id)
    rows = getresult(query['check_alm'], (id,))
    if rows:
        return True


def check_is_reported_by_alm_id(id):
  # for obj use in arg (obj.alarm_detail)
    rows = getresult(query['check_alm_detail'], (id,))
    if rows:
        return True


def check_is_planedwork():
    rows = getresult(query['planed_work'], (datetime.now().strftime("%Y/%m/%d %H:%M:%S"),), allrows = True)
    if rows:
        return [i[0] for i in rows]


# save reported alalrm to db base on list 
def log_alarm_list(list):
    with CursorFromConnectionFromPool() as cr:
        cr.execute(quequery['rec_alm'], (*list))


# save reported alalrm to db base on obj
def log_alarm(obj):
    execquery(query['record_alms'], (
                                datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                                "app_osc",
                                obj.tt,
                                "Ocean",
                                obj.alarm_id,
                                "OSC LOS",
                                obj.timestamp,
                                obj.event_start_time,
                                obj.ne_name,
                                obj.port_loca,
                                obj.wdm_section_name(),
                                find_OT(obj.wdm_section_name()),
                                "NULL",
                                obj.alarm_detail
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



# def find_tt(resource, criticity = 2, priority = 1, category = 'E', days = 5, group_created = '548002'):
#     """
#     Find tickets created by FO: 
#     criticity = [2|3] (Interrupted service|No interference)
#     priority = [1|2|3] (P1|P2|P3)
#     category = [E|B] (Interrupted service|No interference)
#     """
#     Ticket_to_find = Ticket(
#                     criticity = criticity, 
#                     priority = priority, 
#                     category = category,
#                     filterStartDateTime = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ"),
#                     groupId = group_created
#     )
#     finded_tt = Ocean_Api.search_ticket(Ticket_to_find.dict_from_class())
#     if finded_tt:
#         return [i['id'] for i in finded_tt if resource in i['description']]


# def create_tt(**kwargs):
#     """
#     Create ticket base on: 
#     criticity = [2|3] (Interrupted service|No interference)
#     priority = [1|2|3] (P1|P2|P3)
#     category = [E|B] (Interrupted service|No interference)
#     resorce = resorce in Marina DB
#     createStartDateTime = in fomrat '2021-07-02T10:50:22Z'
#     """
#     Ticket_to_create = Ticket(
#                     externalId =  kwargs.get('externalId', 'AutoTN App'), 
#                     criticity = kwargs.get('criticity'),
#                     priority = kwargs.get('priority'),
#                     category = kwargs.get('category'),
#                     description =  kwargs.get('description'),
#                     resorce =  kwargs.get('resorce'),
#                     createStartDateTime = kwargs.get('createStartDateTime'),
#                     groupId = kwargs.get('groupId', '548002'),
#     ) 
#     created_tt = Ocean_Api.create_ticket(Ticket_to_create.dict_from_class())
#     # print(Ticket_to_create.dict_from_class())
#     if created_tt:
#         return created_tt['id']


# def add_comment(ticket, comment):
#     commented_tt =  Ocean_Api.add_comment_to_ticket(ticket, comment)
#     if commented_tt:
#         return commented_tt['id']

# def activate_group(ticket, dest_group_id='548003'):
#     activated_tt = Ocean_Api.activate_gr_for_ticket(ticket, dest_gr_id=dest_group_id)
#     if activated_tt:
#         return activated_tt