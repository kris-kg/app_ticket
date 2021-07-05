import os
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

host_es = os.environ.get("HOST_ES")
user_es = os.environ.get("USER_ES")
port_es = os.environ.get("PORT_ES")
url_pfefix_es = os.environ.get("URL_PREFIX_ES")
pass_es = os.environ.get("PASSWORD_ES")


def time_to_qery(minutes):
    now_time = datetime.now(tz=timezone.utc)
    start_time = now_time - timedelta(minutes = minutes) 
    start_time = start_time.strftime("%Y-%m-%dT%H:%M")
    now_time = now_time.strftime("%Y-%m-%dT%H:%M")
    return now_time, start_time


now_time, start_time = time_to_qery(7880) 


def get_resultes(host =host_es, port = port_es ,url_prefix = url_pfefix_es, user = user_es,
                 password = pass_es, alarm_query ="OSC_LOS", start_query= start_time, end_query= now_time):

  es = Elasticsearch(host, port=port, url_prefix = url_prefix,  http_auth=(user, password))


  body_search = {
  "version": True,
  "size": 500,
  "sort": [
    {
      "@timestamp": {
        "order": "desc",
        "unmapped_type": "boolean"
      }
    }
  ],
    "query": {
        "bool": {
          "must": [],
          "filter": [
             {
              "match_all": {}
            },
            {
              "match_phrase": {
                "usersite.raw": "OSP_ROADM"
              }
            },
            {
              "match_phrase": {
                "probableCause": alarm_query 
              }
            },
          #  {
          # "match_phrase": {
          #   "status.raw": "ACTIVE"
          #     }
          #   },
            {
              "range": {
                "@timestamp": {
                  "gte": start_query,
                  "lte": end_query,
                  "format": "strict_date_optional_time"
                }
              }
            }
          ]
        }
      }
    }
    
  try:
    res = es.search(index="alarms-pool", body=body_search)
    connectoin_status = True
    query_list = res['hits']['hits']
    if query_list:
        print(f"Find {len(query_list)} results")
    else:
      print("Nothing found")    
  except:
      connectoin_status = False
      raise Exception("Connection to ES failed, check query parameters.")
  return query_list