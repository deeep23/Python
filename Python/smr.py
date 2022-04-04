import pandas as pd
import json
import numpy as np
from datetime import datetime


def str2datetime(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')

id = 0
e1 = pd.read_csv("Converse Entity 17-20 March.csv")
e2 = pd.read_csv("Converse Entity 21-23 March.csv")
e3 = pd.read_csv("Converse Entity 24-25 March.csv")
entity1 = pd.concat([e1, e2])
session_table = pd.read_csv("Converse_Session 17-25 March.csv")
session_table = session_table.replace(np.NAN, "NULL")
entity_table = pd.concat([entity1, e3])
entity_table = entity_table.replace(np.NAN, "NULL")
trans_msg_table = pd.read_csv("Converse_non_annonimized 17-25 March.csv",
                              encoding='utf-8')
trans_msg_table = trans_msg_table.replace(np.nan, "NULL")
unique_session = session_table.session_id
summary = pd.DataFrame()
for each_session in unique_session:
    id += 1
    #     if each_session in list(summary.session_id):
    #         continue
    msg_record = ""
    conversation = trans_msg_table[trans_msg_table["session_id"] == each_session][['message', 'start_date_time']]

    #     intent = msg_table[msg_table["session_id"] == each_session][['scenario', 'sub_scenario']]

    unique_entity = entity_table[entity_table['session_id'] == each_session][['session_id', 'entity', 'value']]

    tags = dict()
    last_message = ''

    if each_session not in list(trans_msg_table["session_id"]):
        tags["Not Found in message table"] = 1
        summary = summary.append(tags, ignore_index=True)
        continue
    else:
        tags["Not Found in message table"] = 0

    tags['message_id'] = trans_msg_table[trans_msg_table["session_id"] == each_session][['message_id']].iloc[0, 0]

    tags['session_id'] = each_session

    if "funnel_state" in list(unique_entity.entity):
        funnel = unique_entity[unique_entity['entity'] == 'funnel_state'][['value']].iloc[-1, 0]
        tags['funnel_state'] = funnel

    if "loc_cd" in list(unique_entity.entity):
        loc_cd = unique_entity[unique_entity['entity'] == 'loc_cd'][['value']].iloc[-1, 0]
        tags['loc_cd'] = loc_cd

    if "is_interested_one" in list(unique_entity.entity):
        is_interested_one = unique_entity[unique_entity['entity'] == 'is_interested_one'][['value']].iloc[-1, 0]
        tags['is_interested_one'] = is_interested_one

    if "ask_date_entity_api" in list(unique_entity.entity):
        ask_date_entity_api = unique_entity[unique_entity['entity'] == 'ask_date_entity_api'][['value']].iloc[-1, 0]
        tags['ask_date_entity_api'] = ask_date_entity_api
        if "map" in ask_date_entity_api:
            session = json.loads(ask_date_entity_api)
            sessionObj = session["map"]
            if "prefered_time" in sessionObj:
                tags["prefered_time"] = sessionObj["prefered_time"]
            if " is_interested" in sessionObj:
                tags["is_interested"] = sessionObj[" is_interested"]
            if " prefered_date" in sessionObj:
                tags["prefered_date"] = sessionObj[" prefered_date"]

    if "#log_id" in list(unique_entity.entity):
        log_id = unique_entity[unique_entity['entity'] == '#log_id'][['value']].iloc[-1, 0]
        tags['#log_id'] = log_id

    if "ask_time" in list(unique_entity.entity):
        ask_time = unique_entity[unique_entity['entity'] == 'ask_time'][['value']].iloc[-1, 0]
        tags['ask_time'] = ask_time

    if "#calling_no" in list(unique_entity.entity):
        calling_no = unique_entity[unique_entity['entity'] == '#calling_no'][['value']].iloc[-1, 0]
        tags['#calling_no'] = calling_no

    intent_dict = dict()

    start_at = str2datetime(conversation['start_date_time'].iloc[0,])

    for msg_len in range(len(conversation)):
        if (msg_len % 2 == 0):
            msg_record = msg_record + "User: " + conversation['message'].iloc[msg_len,] + " Time: " + str(
                (str2datetime(conversation['start_date_time'].iloc[msg_len,]) - start_at).total_seconds()) + "\n"
            if '~CDR' not in conversation['message'].iloc[msg_len,] and 'sipheader' not in conversation['message'].iloc[
                msg_len,]:
                last_message = conversation['message'].iloc[msg_len,]
        else:
            msg_record = msg_record + "Bot: " + conversation['message'].iloc[msg_len,] + " Time: " + str(
                (str2datetime(conversation['start_date_time'].iloc[msg_len,]) - start_at).total_seconds()) + "\n"
    tags['message'] = msg_record
    if msg_len >= 2:
        if '~CDR' not in conversation['message'].iloc[2,] and 'sipheader' not in conversation['message'].iloc[2,]:
            tags['first_message'] = conversation['message'].iloc[2,]
    else:
        tags['first_message'] = ""

    tags['last_message'] = last_message

    tags['intent_message'] = intent_dict

    if "rezo_session_id" in list(unique_entity.entity):
        rezo_session_id = unique_entity[unique_entity['entity'] == 'rezo_session_id'][['value']].iloc[0, 0]
        tags['call_start_at'] = datetime.fromtimestamp((int(str(rezo_session_id).split("-")[0]) - 19800000) / 1e3)

    tags['call_ended_at'] = str2datetime(conversation['start_date_time'].iloc[msg_len,])

    if "cdr" in list(unique_entity.entity):
        cdr_seconds = unique_entity[unique_entity['entity'] == 'cdr'][['value']].iloc[-1, 0]
        tags['cdr_seconds_entity'] = cdr_seconds
    summary = summary.append(tags, ignore_index=True)
    print(id)
summary.to_csv('summary_smr.csv', index=False, encoding='utf-8')