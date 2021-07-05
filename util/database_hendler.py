from .database import CursorFromConnectionFromPool


query = {
'record_alms': 'INSERT INTO "tickets_alarm" ("time_reported", "ticket_app", "ticket_id", "reported_to_tt", "es_alarm_id", "probableCause", "timestamp_NFM", \
        event_start_time, "ne_name", "ne_port", "link", "ot", "remarks", "alarm_detail") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
'check_alm': 'SELECT "es_alarm_id" FROM "tickets_alarm" WHERE "es_alarm_id" = %s',
'check_alm_detail' : 'SELECT "alarm_detail" FROM "tickets_alarm" WHERE "alarm_detail" = %s',
'source_port' : 'SELECT * FROM tx_wdm_hua_cable WHERE "Source_NE" =%s AND "Source_Port" LIKE %s',
'sink_port' : 'SELECT * FROM tx_wdm_hua_cable WHERE "Sink_NE" =%s AND "Sink_Port" LIKE %s',
'ot': """SELECT id_trail, id_trail_proteccion, nodo_a, nodo_z, n_serie, señal FROM giros_trails_extendidos_light WHERE \
        "nodo_a" =%s AND "nodo_z" =%s AND "n_serie" =%s AND "señal" = 'WDM'""",
'gis': """SELECT "SERVICE", "TRAIL", "FROM_EQUIPMENT_NAME", "FROM_HUB", "TO_EQUIPMENT_NAME", "TO_HUB" FROM "GIS_NE_exp04_route" WHERE "TRAIL" LIKE  %s""",
'planed_work': """SELECT l."Name" FROM "planedwork_links" as l INNER JOIN "planedwork_planedworkresource" as r ON r.resurce_id = l.id \
        INNER JOIN "planedwork_planedwork" as p ON  r.planedwork_id = p.id WHERE  p.time_end  >= %s and r.affected = '1'"""
}

def getresult(query, parms, allrows = False):
        with CursorFromConnectionFromPool() as cr:
                cr.execute(query, parms)
                if allrows:
                        result = cr.fetchall()
                else:
                        result = cr.fetchone()
                return result


def execquery(query, parms):
	with CursorFromConnectionFromPool() as cr:
        	cr.execute(query, parms)
