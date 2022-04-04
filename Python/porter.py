import pandas as pd
import json
import numpy as np
from datetime import datetime

import json


def get_distinct_sessions(input_file):
    unique_sessions = set()
    df = pd.read_csv(input_file)

    df = df.replace(np.NAN, "NA")

    ids = df.messageID.unique()
    print("Len of Unique Sessions : " + str(len(ids)))
    return df, ids


def process_data(input_file):
    df, distint_sessions = get_distinct_sessions(input_file)

    summary = pd.DataFrame()

    break_at = 100
    id = 0
    for each_session in distint_sessions:
        if len(each_session) < 16 or "8696999993" in each_session or "9711006419" in each_session or "7500081003" in each_session:
            continue
        id += 1
        total_conversation = df[df['messageID'] == each_session]
        filtered_data = pd.DataFrame()

        tags = dict()

        # init variables
        list_filled_intent = []
        final_intent = ""
        all_messages = ""

        # DATE AND DATA FORMAT PENDINGF

        counter_silence_found = 0
        total_messages = 0
        start_at_date_time = None
        end_at_date_time = None
        start_at_date = None
        start_at_time = None
        user_word_count = 0
        transfer_request = 0

        for index, row in total_conversation.iterrows():

            if "sipheader" not in row["message"] and "CDR" not in row["message"] and "Conference" not in row["message"]:
                total_messages += 1

            if "silencefound" in row["message"]:
                counter_silence_found += 1

            if "CONFERENCE" in row["response"]:
                tags["call_type"] = "CONFERENCE"
            elif "TRANSFER" in row["response"]:
                tags["call_type"] = "TRANSFER"
            elif "~HANGUP" in row["response"]:
                tags["call_type"] = "BOT-HANGUP-FlowEnd"
            elif "transfer" in row["category"]:
                tags["call_type"] = "TransferRequestedbyDriver"

            # get the first CDR / ConferenceStart to detect cdr_seconds
            if ("ConferenceStarted" in row["message"] or "CDR" in row["message"]) and "cdr_secods" not in tags:
                cdr_resp = row["message"].split("_")

                end_at_date_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')

                if (len(cdr_resp) > 1):
                    tags["cdr_secods"] = int(cdr_resp[1]) / 1000

            if "sipheader" in row["message"]:
                start_at_date_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')
                start_at_date = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                start_at_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ').time()

            if "sipheader" not in row["message"] and "CDR" not in row["message"] and "Conference" not in row["message"]:
                user_word_count += len(
                    row["message"].replace("|", "").replace("!", "").replace("?", "").replace(".", "").split())
            all_messages = all_messages + "User: " + row["message"] + "\n Bot: " + row["response"] + "\n"

            # get cases where handover happened:
            # print(row["handover"])
            if "Counter Reached" in row["handover"] and "handover_case" not in tags and "CDR" not in row["message"]:
                tags["handover_case"] = row["message"]

            session = json.loads(row["rezoSession"])

            if "sessionObj" in session:
                sessionObj = session["sessionObj"]

                if "handover_desc" in sessionObj:
                    handover_desc = sessionObj["handover_desc"]
                    tags["handover_desc"] = handover_desc

                if "funnel_state" in sessionObj:
                    funnel_state = sessionObj["funnel_state"]
                    tags["funnel_state"] = funnel_state

                if "rec_url" in sessionObj:
                    rec_url = sessionObj["rec_url"]
                    tags["rec_url"] = rec_url

            if row["category"] is not "" and row["category"] != "NA" and "sipheader" not in row[
                "message"] and "CDR" not in row["message"] and "Conference" not in row["message"]:
                if "intent_messages" in tags:
                    intent_messages = tags["intent_messages"]
                else:
                    intent_messages = {}

                intent_messages[row["message"]] = row["category"] + "_" + row["sub_category"] + "_" + str(
                    row["confidence"])
                tags["intent_messages"] = intent_messages

                if row["category"] != "greet":
                    tags["final_intent"] = row["category"] + "_" + row["sub_category"]

            if "Conference" in row["message"]:
                filtered_data = filtered_data.append(row, ignore_index=True)
                break
            else:
                filtered_data = filtered_data.append(row, ignore_index=True)
            if "transfer" in row["category"]:
                transfer_request = 1

        if "handover_case" not in tags and "call_type" not in tags:
            tags["call_type"] = "User Dropped"

        tags["session_id"] = each_session
        tags["list_filled_intent"] = str(list_filled_intent)
        tags["all_messages"] = all_messages
        tags["transfer_request"] = transfer_request
        if total_messages != 0:
            tags["unresponiveness"] = counter_silence_found / total_messages * 100
        else:
            tags["unresponiveness"] = 0

        tags["call_start_at"] = start_at_date_time
        tags["call_end_at"] = end_at_date_time
        tags["silence_count"] = counter_silence_found
        tags["total_message_count"] = total_messages
        tags["user_word_count"] = user_word_count
        print(str(tags))
        summary = summary.append(tags, ignore_index=True)

        print("here")
        summary.to_csv('summary_porter.csv', encoding='utf-8', index=False)
        # if (id>break_at):
        #    break
        


if __name__ == "__main__":
    input_file = 'C://Users//HR OFFICE//Downloads//Porter_Data_19th_20thFeb 8.csv (1)//Porter_Data_19th_20thFeb.csv'
    process_data(input_file)