import pandas as pd
import json
import numpy as np
from datetime import datetime
from csv import writer

def get_distinct_sessions(input_file):
    unique_sessions = set()
    df = pd.read_csv(input_file)

    df = df.replace(np.NAN,"NA")

    ids = df.messageID.unique()
    print("Len of Unique Sessions : " + str(len(ids)))
    return df,ids

def process_data(input_file):
    df,distint_sessions = get_distinct_sessions(input_file)

    summary = pd.DataFrame()

    break_at = 100
    id = 0
    with open('summary_psf_text.csv', 'a') as summary_txt:
        writer_obj = writer(summary_txt, delimiter=',', lineterminator='\n')
        for each_session in distint_sessions:
            id +=1
            total_conversation = df[df['messageID'] == each_session]
            filtered_data =pd.DataFrame()

            tags = dict()

            #init variables
            list_filled_intent = []
            final_intent = ""
            all_messages = ""

            #DATE AND DATA FORMAT PENDINGF

            counter_silence_found = 0
            total_messages = 0
            start_at_date_time = None
            end_at_date_time = None
            start_at_date = None
            start_at_time = None
            first_message = None
            first_message_cat = None
            txt_call_type = ""
            txt_cdr_seconds = ""
            txt_handover_case = ""
            txt_handover_desc = ""
            txt_funnel_state = ""
            txt_rec_url = ""
            txt_matched_word = ""
            txt_matched_word_time = ""
            txt_feedback = ""
            txt_log_id=""
            txt_callid=""
            txt_intent_messages=""
            txt_final_intent=""
            txt_all_messages=""
            txt_list_filled_intent=""
            txt_session_id=""
            txt_unresponiveness=""
            txt_call_start_at=""
            txt_call_end_at = ""
            txt_first_message=""
            txt_first_message_cat = ""


            for index, row in total_conversation.iterrows():


                if "sipheader" not in row["message"] and "CDR" not in row["message"] and "Conference" not in row["message"]:
                    total_messages +=1
                    if total_messages == 1:
                        first_message = row["message"]
                        if row["category"] is not "" and row["category"] != "NA":
                            first_message_cat = row["category"] + "_" + row["sub_category"]

                if "silencefound" in row["message"]:
                    counter_silence_found +=1

                if "CONFERENCE" in row["response"]:
                    tags["call_type"] = "CONFERENCE"
                    txt_call_type = "CONFERENCE"
                elif "TRANSFER" in row["response"]:
                    tags["call_type"] = "TRANSFER"
                    txt_call_type = "TRANSFER"
                elif "~HANGUP" in row["response"]:
                    tags["call_type"] = "BOT-HANGUP-FlowEnd"
                    txt_call_type = "BOT-HANGUP-FlowEnd"

                #get the first CDR / ConferenceStart to detect cdr_seconds
                if ("ConferenceStarted" in row["message"] or "CDR" in row["message"] ) and "cdr_secods" not in tags:
                    cdr_resp = row["message"].split("_")

                    end_at_date_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')

                    if(len(cdr_resp)>1):
                        tags["cdr_seconds"] = int(cdr_resp[1])/1000
                        txt_cdr_seconds = int(cdr_resp[1])/1000

                if "sipheader" in row["message"]:
                    start_at_date_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    start_at_date = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                    start_at_time = datetime.strptime(row["rezo_recievedAt"], '%Y-%m-%dT%H:%M:%S.%fZ').time()


                all_messages = all_messages + "User: " + row["message"] + "\n Bot: " + row["response"] + "\n"


                #get cases where handover happened:
                #print(row["handover"])
                if "handover" in row and "Counter Reached" in row["handover"] and "handover_case" not in tags and "CDR" not in row["message"]:
                    tags["handover_case"] = row["message"]
                    txt_handover_case = row["message"]


                session = json.loads(row["rezoSession"])



                if "sessionObj" in session:
                    sessionObj = session["sessionObj"]

                    if "handover_desc" in sessionObj:
                        handover_desc = sessionObj["handover_desc"]
                        tags["handover_desc"] = handover_desc
                        txt_handover_desc = handover_desc


                    if "funnel_state" in sessionObj:
                        funnel_state = sessionObj["funnel_state"]
                        tags["funnel_state"] = funnel_state
                        txt_funnel_state = funnel_state

                    if "rec_url" in sessionObj:
                        rec_url = sessionObj["rec_url"]
                        tags["rec_url"] = rec_url
                        txt_rec_url = rec_url


                    if "matched_word" in sessionObj:
                        tags["matched_word"] = sessionObj["matched_word"]
                        txt_matched_word = sessionObj["matched_word"]
                        tags["matched_word_time"] = row["rezo_recievedAt"]
                        txt_matched_word_time = row["rezo_recievedAt"]

                    if "feedback" in sessionObj:
                        tags["feedback"] = sessionObj["feedback"]
                        txt_feedback = sessionObj["feedback"]

                    if "log_id" in sessionObj:
                        tags["log_id"] = sessionObj["log_id"]
                        txt_log_id = sessionObj["log_id"]

                    if "callid" in sessionObj:
                        tags["callid"] = sessionObj["callid"]
                        txt_callid = sessionObj["callid"]



                if row["category"] is not "" and row["category"] != "NA" and "sipheader" not in row["message"] and "CDR" not in row["message"] and  "Conference" not in row["message"]:
                    if "intent_messages" in tags:
                        intent_messages = tags["intent_messages"]
                    else:
                        intent_messages = {}

                    intent_messages[row["message"]] = row["category"] + "_" + row["sub_category"] + "_" + str(row["confidence"])
                    tags["intent_messages"] = intent_messages
                    txt_intent_messages = intent_messages

                    if row["category"] != "greet":
                        tags["final_intent"] = row["category"] + "_" + row["sub_category"]
                        txt_final_intent = row["category"] + "_" + row["sub_category"]

                if "Conference" in row["message"]:
                    filtered_data= filtered_data.append(row, ignore_index= True)
                    break
                else:
                    filtered_data= filtered_data.append(row, ignore_index= True)



            if "handover_case" not in tags and "call_type" not in tags:
                tags["call_type"] = "User Dropped"
                txt_call_type = "User Dropped"



            tags["session_id"] = each_session
            txt_session_id = each_session
            tags["list_filled_intent"] = str(list_filled_intent)
            txt_list_filled_intent = str(list_filled_intent)
            tags["all_messages"]  = all_messages
            txt_all_messages = all_messages


            if total_messages != 0:
                tags["unresponiveness"] = counter_silence_found /total_messages * 100
                txt_unresponiveness = counter_silence_found /total_messages * 100
            else:
                tags["unresponiveness"] = 0
                txt_unresponiveness = 0

            tags["call_start_at"] = start_at_date_time
            txt_call_start_at = start_at_date_time
            tags["call_end_at"] = end_at_date_time
            txt_call_end_at = end_at_date_time
            tags["first_message"] = first_message
            txt_first_message = first_message
            tags["first_message_cat"] = first_message_cat
            txt_first_message_cat = first_message_cat
            print(str(tags))
            summary = summary.append(tags,ignore_index=True)



            obj_list = [txt_call_type,txt_cdr_seconds,txt_handover_case,txt_handover_desc,txt_funnel_state,txt_rec_url,
                        txt_matched_word,txt_matched_word_time,txt_feedback,txt_log_id,txt_callid,txt_intent_messages,
                        txt_final_intent,txt_all_messages,txt_list_filled_intent,txt_session_id,txt_unresponiveness,
                        txt_call_start_at,txt_call_end_at,txt_first_message,txt_first_message_cat]

            writer_obj.writerow(obj_list)
            print(str(id))

            if (id>break_at):
               break
        summary_txt.close()
    summary.to_csv('summary_psf.csv', encoding='utf-8', index=False)



if __name__ == "__main__":
    #input_file = 'data/Porter_Data_19th_20thFeb.csv'
    input_file = 'C://Users//HR OFFICE//Downloads//PSF_20-21_Data//PSF_20-21_Data.csv'
    process_data(input_file)