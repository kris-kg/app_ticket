from datetime import datetime
from .database import CursorFromConnectionFromPool
import re
from .base_function import (
                        switch_ends_wdm,
                        get_fiber_date,
                        find_OT,
                        find_GIS,
                        query_source_port,
                        query_sink_port,
                        ot
)


class Alarm():
    alarm_id = None
    event_update_time = None
    port_loca = None
    ne_name = None
    alarm_object = None   
    alarm_source = None
    port_name = None
   
      
    def __init__(self, result_query):
        if result_query == None: 
            raise Exception("You must set a query")
        assert isinstance(result_query, dict)
        self.alarm_id =  result_query['_id']
        self.timestamp = result_query['_source']['@timestamp']
        self.location = result_query['_source']['location']
        self.ne = result_query['_source']['ne']
        self.ne_type = result_query['_source']['ne_type']
        self.event_start_time = result_query['_source']['event_start_time']
        self.event_update_time = result_query['_source']['event_update_time']
        self.port_loca = result_query['_source']['nePort'] 
        self.ne_name = result_query['_source']['ne_name']
        self.alarm_object = result_query['_source']['object']
        self.alarm_detail = result_query['_source']['detail']
        
    def __str__(self):
        return self.port_loca
                  
        
    def alarm_source_name(self):
        alarm_source = f"{self.ne_name} / {self.alarm_object.split('OSP_')[-1]}"
        self.alarm_source = alarm_source
        return alarm_source
        
    
    def set_port_name(self):
        patern = r"(?P<shelf>^\d+)-(?P<descrip>.+)-(?P<slot>\d+)-(?P<card>.+)-(?P<port>\d+)(?P<port_2>.+)-(?P<type>\w+):\d*"
        regex = re.compile(patern)
        my_match = regex.match(self.port_loca)
        if my_match == None:
            port_name = None
        else:
            port_name = f"{self.alarm_object.split('OSP_')[-1]}-Shelf{my_match['shelf']}-{my_match['slot']}-{my_match['card']}-{my_match['port']}{my_match['port_2']}"
        self.port_name = port_name
        return port_name
     
    # make dictionary to query db
    @staticmethod
    def get_port_attribute(port):
        patern = r"(?P<shelf>.+)-(?P<slot>.+)-(?P<card>.+)-(?P<port>\d+)(?P<port_2>.+)"
        regex = re.compile(patern)
        my_match = regex.match(port.split("-", 1)[1])
        if my_match:
            return { 'ne': port.split("-", 1)[0], 'shelf': f"{my_match['shelf']}",
                'slot': my_match['slot'], 'card': my_match['card'], 'port': my_match['port'], 'port2': my_match['port_2']}



class OscAlarm(Alarm):
    
    section_wdm = None
    oa_port1 = None
    oa_port2 = None
    port_info = None
     
    
    def port_osc_oa(self):
        matches =  ["FIU", "DAS", "DAP"]
        if not self.port_name:
            self.set_port_name()
        dane = self.get_port_attribute(self.port_name)
        port = get_fiber_date(dane)
        if port and any(x in port['Sink_Port'] for x in matches):
            port_osc_oa = f"{port['Sink_NE']}-{port['Sink_Port']}"
            return port_osc_oa
        else:
            port = get_fiber_date(dane, q = query_sink_port)
        if port and any(x in port['Source_Port'] for x in matches):
            port_osc_oa = f"{port['Source_NE']}-{port['Source_Port']}"
            return port_osc_oa
                      
    
    def oa_port_name1(self):
        if self.oa_port1 == None:
            port = self.port_osc_oa()
            if port:
                patern = r"(?P<ne_shelf>.+-Shelf\d+-\d+)-(?P<card>\d+[A-Z]+\d+|[A-Z]+\d+|\d+[A-Z]+)-(.+)"
                regex = re.compile(patern)
                try:
                    my_match = regex.match(port)
                except:
                    my_match = None
                if my_match:
                    if "FIU" in my_match['card']:
                        oa_oa_port = f"{my_match['ne_shelf']}-{my_match['card']}-1(IN/OUT)"
                    elif "DAS" in my_match['card']:       
                        oa_oa_port = f"{my_match['ne_shelf']}-{my_match['card']}-1(LIN/LOUT)"       
                    elif "DAP" in my_match['card']:
                        oa_oa_port = f"{my_match['ne_shelf']}-{my_match['card']}-11(LIN/LOUT)" 
                    else:
                        oa_oa_port = None     
                else:
                    oa_oa_port = None
                    print("oa_port_name nothing found")
            
            else:
                oa_oa_port = None
            self.oa_port1 = oa_oa_port
            return oa_oa_port
        else:
            return self.oa_port1
        
        
    def oa_port_section(self):
        if self.oa_port2 and self.section_wdm:
            return self.oa_port2, self.section_wdm 
        if not self.oa_port1:
            oa_oa_port1 = self.oa_port_name1()
        if self.oa_port1:
            dane = self.get_port_attribute(self.oa_port1)
            port = get_fiber_date(dane)
            if port:
                self.oa_port2 = f"{port['Sink_NE']}-{port['Sink_Port']}"
                self.section_wdm = f"{port['Name']}"
                return self.oa_port2, self.section_wdm 
            else:
                port = get_fiber_date(dane, q = query_sink_port)
                self.oa_port2 = f"{port['Source_NE']}-{port['Source_Port']}"
                self.section_wdm = f"{port['Name']}"
                return self.oa_port2, self.section_wdm 
        else:
            self.oa_port2 = None
            self.section_wdm = None
            return self.oa_port2, self.section_wdm 


    def wdm_section_name(self):
        if self.section_wdm and "WDM" in self.section_wdm:
            return self.section_wdm
        _ , self.section_wdm = self.oa_port_section()
        if self.section_wdm and "WDM" in self.section_wdm:
            return self.section_wdm


    def oa_port_name2(self):
        if self.oa_port2:
            return self.oa_port2
        port, _ = self.oa_port_section()
        return port

        
    def render(self):
        dict = {
        "data_field": datetime.now().strftime("%H:%M %Y:%m:%d"),
        "alarm_id": self.alarm_id,
        "event_report_time": self.event_update_time,
        "Alarm port": self.set_port_name(),
        "ne_name": self.alarm_source_name(),
        "alarm_source": self.port_loca,
        "port_name": self.port_name,   
        "1end_node": self.oa_port_name1().split('-Shelf')[0] if self.oa_port_name1() != None else None,
        "1end_port": self.oa_port_name1(),
        "2end_node": self.oa_port_name2().split('-Shelf')[0] if self.oa_port_name2() != None else None,   
        "2end_port": self.oa_port_name2(),   
        "wdm_section": self.wdm_section_name(),
        "ot": f"{ot}{find_OT(self.section_wdm)}",
        "gis": find_GIS(self.section_wdm),
        "Emplazamiento": self.location,
        "Name SEDRA": self.ne
            }
        return dict
        


