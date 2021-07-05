import requests
from datetime import datetime, timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from dotenv import load_dotenv
from pathlib import Path


BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# environment variables
client_id = os.environ.get("OCEAN_CLIENT_ID")
client_secret = os.environ.get("OCEAN_CLIENT_SECRET")
app_id = os.environ.get("OCEAN_APP_ID")
aut_header = os.environ.get("OCEAN_AUTH_HEADER")
ocean_id = os.environ.get("OCEAN_CUID")

api_host = "https://inside01.api.intraorange"
api_base_url = "troubleticket_sandbox_b2b"
api_ver = "v1"
api_app = "troubleTicket"

api_url = f"{api_host}/{api_base_url}/{api_ver}/{api_app}"

class Token:
    token_start_time = None
    __access_token = None
    endpoint  = "https://inside01.api.intraorange/oauth/v3/token"
    payload="grant_type=client_credentials"
    header = {
        'Authorization': "#######",
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    @classmethod
    def getToken(cls):
        if cls.__access_token and cls.token_start_time > datetime.now() - timedelta(seconds = 3600): 
            return cls.__access_token 
        cls.token_start_time = datetime.now()
        r = requests.post(cls.endpoint, headers=cls.header, data=cls.payload, verify=False)
        if r.status_code in range(200, 299):
            cls.__access_token = r.json()['access_token']
            return cls.__access_token
        print(f"{r.status_code} Wrong request")
        
    @classmethod
    def logout(cls):
        pass



class Ocean_Api():
    header = {  
        'Accept': 'application/json;charset=utf-8',
        'X-Client-User-Id': ocean_id3,
      }

    @classmethod
    def search_ticket(cls, payload_tt):
        cls.header['Authorization'] = f'Bearer {Token.getToken()}'
        url = f"{api_url}/search?offset=0&limit=50"
        r = requests.post(url, headers=cls.header, data=str(payload_tt), verify = False)
        if r.status_code in range(200, 299):
            return r.json()
        print(f"{r.status_code} Wrong request")

    @classmethod
    def create_ticket(cls, payload_tt):
        cls.header['Authorization'] = f'Bearer {Token.getToken()}'
        url = f"{api_url}"
        r = requests.post(url, headers=cls.header, data=str(payload_tt), verify = False)
        if r.status_code in range(200, 299):
            return r.json()
        print(f"{r.status_code} Wrong request")
    
    @classmethod
    def activate_gr_for_ticket(cls, ticket, src_gr_id='548002', dest_gr_id='548003', role='TroubleResolutionContributor'):
        cls.header['Authorization'] = f'Bearer {Token.getToken()}'
        url = f"{api_url}/{ticket}/partyIntervention"
        payload = { 
                    "level": 1,
                    "requestorId": src_gr_id,
                    "relatedParty":{ "id": dest_gr_id, "role": role},
                    "activation": "true"
                    }
        r = requests.post(url, headers=cls.header, data=str(payload), verify = False)
        if r.status_code in range(200, 299):
            return r.json()
        print(f"{r.status_code} Wrong request")

    @classmethod
    def add_comment_to_ticket(cls, ticket, text, author="AUTOTN01"):
        cls.header['Authorization'] = f'Bearer {Token.getToken()}'
        cls.header['X-HTTP-Method-Override'] = 'PATCH'
        url = f"{api_url}/{ticket}"
        payload = {
                    "note": [
                                {
                                    "author": author,
                                    "text": text,
                                    "commentType": {"id": "INT", 'label': 'Internal'},
                                    "operationType": {"id": 9}
                                }
                            ]
                    }
        r = requests.put(url, headers=cls.header, data=str(payload), verify = False)
        if 'X-HTTP-Method-Override' in cls.header:
            del cls.header['X-HTTP-Method-Override']
        if r.status_code in range(200, 299):
            return r.json()
        print(f"{r.status_code} Wrong request")



class Ticket():   
    """
    externalId/Third party reference: 'AutoTN App', 
    ticketType: {'id': '1', 'label': 'Failure'}
    criticity: {'id': 2, 'label': 'Interrupted service'}/{'id': 3, 'label': 'No interference'}
    priority: {'id': 1 'label': 'P1'}/{'id': 2 'label': 'P2'}
    category: {'id': 'E', 'label': 'Interrupted service'}/{'id': 'B', 'label': 'No interference'},
    startDateTime: .strftime("%Y-%m-%d-T%H:%M:%SZ")
    troubleTicketCharacteristic: 
        symptomDetail: {'id': '614'} = 'OSP-TRANSMISION'
        symptomFamily: {'id': '61409'}= 'RED TRANSPORTE/WDM'
    """

    def __init__(self, id = None, externalId = None, description = None, criticity = None, priority = None,
                 category = 'E', createStartDateTime = None, filterStartDateTime = None, resorce = None, groupId = '548002',
                 symptomDetail = '61409', symptomFamily = '614'):
    
        self.id = id
        self.externalId = externalId 
        self.description = description
        self.ticketType = {'id': '1'}
        self.criticity= {'id': criticity } if priority else None
        self.priority= {'id': priority } if priority else None
        self.origin = {'id': '2', 'label': 'Supervision'}
        self.category = {'id': category} if priority else None
        if createStartDateTime:
            self.status = {
                        "code": "InProgress",
                        "isCurrentStatus": 'true',
                        "startDateTime": createStartDateTime 
                }
        if filterStartDateTime:
            self.status = [{
                        "code": "InProgress",
                        "isCurrentStatus": 'true',
                        "startDateTime": filterStartDateTime 
                }]
        self.troubleTicketCharacteristic =  [{'name': 'symptomDetail', 'id': symptomDetail},  {'name': 'symptomFamily', 'id': symptomFamily}]
        if resorce:
            self.relatedResource =  {"resourceSpecCharacteristic":[{'index': '1', 'id': 'OSP_NENAME','value': resorce}]}
        if groupId:
            self.relatedParty = [{ 'id': groupId, 'role': 'TroubleResolutionLeader'},]
        
    def set_resorce(self, resorce):
        if resorce:
            self.relatedResource =  {"resourceSpecCharacteristic":[{'index': '1', 'id': 'OSP_NENAME','value': resorce}]}
        
    def dict_from_class(self):
        return dict(
        (key, value)
        for (key, value) in self.__dict__.items()
            if value is not None
        )

