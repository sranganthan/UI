#!/bin/bash
#The script is used to generate the Definitive bill Text file generation 

# Prevent multiple instances of this script
SCRIPT_NAME=$(basename "$0")
RUNNING_COUNT=$(ps -ef | grep "$SCRIPT_NAME" | grep -v grep | grep -v $$ | wc -l)

if [ "$RUNNING_COUNT" -gt 0 ]; then
  echo "ERROR: $SCRIPT_NAME is already running. Only one instance is allowed."
  exit 1
fi


# Define environment variables
HERE=$(pwd)
datehrs=$(date "+%Y%m%d_%H%M%S")
LOG_DIR="${HERE}/log"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/Definitive_log__${datehrs}.log"

# Define config paths
PATH_CONFIG="/appl_sw/custbill/CONFIG/"
CONFIG_FILE="ConfigDb.cfg"
GET_CONF="${PATH_CONFIG}GetConfVal.sh"
ARBORBIN="/appl_sw/custbill/BIN"
export ARBORBIN



# Logging function
echolog() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*"
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG_FILE"
}

read -p "Enter the Account no to run Definitive: " account_no

# Get DB credentials using GetConfVal.sh
conf_name_input="ARBCUST_6"
CONF_RESULT_INPUT=$($GET_CONF "$CONFIG_FILE" "$conf_name_input" "USERNAME:PWD:SID" 1)
IFS=":" read -r INPUT_DB_USER INPUT_DB_PASS INPUT_DB_SID <<< "$CONF_RESULT_INPUT"

# Get server_id from DB
echolog "Fetching server_id for account_no=$account_no"
server_id=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT server_id FROM external_id_acct_map@KCA1 WHERE account_no = '$account_no' AND ROWNUM = 1;
EXIT;
EOF
)

server_id=$(echo "$server_id" | xargs)

if [[ -z "$server_id" || "$server_id" == *"ORA-"* ]]; then
  echolog "Failed to fetch valid server_id. Check if table exists and account_no is valid."
  exit 1
fi

echolog "server_id=$server_id"

# Determine db_index based on server_id
case $server_id in
  3) db_index=1 ;;
  4) db_index=2 ;;
  5) db_index=3 ;;
  6) db_index=4 ;;
  7) db_index=5 ;;
  8) db_index=6 ;;
  *) echolog "Unknown server_id: $server_id"; exit 1 ;;
esac

DB_ALIAS="COKCU${db_index}"

# Get updated DB credentials for dynamic alias
conf_name_input="ARBCUST_${db_index}"
CONF_RESULT_INPUT=$($GET_CONF "$CONFIG_FILE" "$conf_name_input" "USERNAME:PWD:SID" 1)
IFS=":" read -r INPUT_DB_USER INPUT_DB_PASS INPUT_DB_SID <<< "$CONF_RESULT_INPUT"

# Set db_index and db_name based on server_id
case $server_id in
  3) db_index=3; db_name="COKCU1" ;;
  4) db_index=4; db_name="COKCU2" ;;
  5) db_index=5; db_name="COKCU3" ;;
  6) db_index=6; db_name="COKCU4" ;;
  7) db_index=7; db_name="COKCU5" ;;
  8) db_index=8; db_name="COKCU6" ;;
  *) echolog "Unknown server_id: $server_id"; exit 1 ;;
esac

# Check account type (TV or BB) and deriving the group id

echolog "Checking the External_ID_Type of the account"
acct_types=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT DISTINCT external_id_type FROM external_id_acct_map@KCA1 WHERE account_no = '$account_no';
EXIT;
EOF
)

acct_types=$(echo "$acct_types" | xargs)

echolog "Account has types: $acct_types"

if [[ "$acct_types" == *"51"* && "$acct_types" == *"61"* ]]; then
  echolog "Account has both TV and BB. Defaulting to TV."
  group_id="1$((server_id - 2))"
elif [[ "$acct_types" == *"51"* ]]; then
  echolog "Account type: TV"
  group_id="1$((server_id - 2))"
elif [[ "$acct_types" == *"61"* ]]; then
  echolog "Account type: BB"
  group_id="3$((server_id - 2))"
elif [[ "$acct_types" == *"71"* ]]; then
  echolog "This is LLAMA Account, Please proceed for Wrapper LLAMA Execution, Exiting the Script"
  exit 1
elif [[ "$acct_types" == *"81"* ]]; then
  echolog "This is LLAMA Account, Please proceed for Wrapper LLAMA Execution, Exiting the Script"
  exit 1
else
  echolog "ERROR: Unsupported account types: $acct_types"
  exit 1
fi

#Check whether the account is valid or not in cmf table
echolog "Checking no_bill and date_inactive columns in cmf table"

checks=$(sqlplus -s "${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID}" <<EOF
set heading off feedback off verify off
SELECT count(*) FROM cmf WHERE account_no=${account_no}
AND no_bill=0 AND date_inactive IS NULL;
EXIT;
EOF
)

# Trim
checks=$(echo "$checks" | xargs)

if [ "$checks" -eq 0 ]; then
  echolog "ERROR: Account either does not exist or is set to no_bill or date_inactive is not null in cmf table. Kindly check your account."
  exit 1
fi

echolog "no_bill=0 and date_inactive is null in cmf table, Proceeding further steps"

echolog "Running BIP for the Test Account"


export ARBORBIN=/appl_sw/kenan_sw/KFX4.0-1/bin
"$ARBORBIN/runbip" bip01 0 "$db_index" "CMF.account_no = $account_no" 


# Get statement date
echolog "Fetching statement date"
link_id=$((server_id - 2))
db_link="COKCU${link_id}"

statement_date=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT MAX( to_char(statement_date,'YYYYMMDD')) FROM bill_invoice@$db_link WHERE account_no=$account_no
and trunc(prep_date)=trunc(sysdate)
 AND prep_status = 1
  AND prep_error_code IS NULL;
EXIT;
EOF
)

statement_date=$(echo "$statement_date" | xargs)
echolog "statement_date=$statement_date"

if [ -z "$statement_date" ]; then
  echolog "ERROR: No valid statement_date found for account_no=${account_no} with prep_status=1 and no prep_error_code.Kindly check the bill_invoice table and log file for /appl_sw/kenan_sw/KFX4.0-1/data/log, Exiting now."
  exit 1
fi



# Map group_id to range values
case $group_id in
  11) start_val=250000001; end_val=300000000 ;;
  12) start_val=300000001; end_val=350000000 ;;
  13) start_val=400000001; end_val=450000000 ;;
  14) start_val=500000001; end_val=550000000 ;;
  15) start_val=600000001; end_val=650000000 ;;
  16) start_val=800000001; end_val=850000000 ;;
  31) start_val=2500000201; end_val=2599999999 ;;
  32) start_val=3500000201; end_val=3599999999 ;;
  33) start_val=4500000201; end_val=4599999999 ;;
  34) start_val=5500000201; end_val=5599999999 ;;
  35) start_val=6500000201; end_val=6599999999 ;;
  36) start_val=8500000201; end_val=8599999999 ;;
  *) echolog "ERROR: Unknown group_id=$group_id"; exit 1 ;;
esac

echolog "Fetching next SIN sequence for group_id=$group_id"
next_sin_seq=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT NVL(MAX(full_sin_seq)+1, $start_val) FROM sin_seq_no@$db_link
WHERE group_id = $group_id
AND full_sin_seq BETWEEN $start_val AND $end_val;
EXIT;
EOF
)

next_sin_seq=$(echo "$next_sin_seq" | xargs)
echolog "Next SIN sequence: $next_sin_seq"

echolog "Fetching billing details from bill_invoice for account_no=$account_no"
read BILL_REF_NO BILL_REF_RESETS PREP_DATE STATEMENT_DATE PAYMENT_DUE_DATE <<< $(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT BILL_REF_NO, BILL_REF_RESETS,
TO_CHAR(PREP_DATE,'DD-MON-RR'),
TO_CHAR(STATEMENT_DATE,'DD-MON-RR'),
TO_CHAR(PAYMENT_DUE_DATE,'DD-MON-RR')
FROM bill_invoice@$db_link
WHERE account_no=$account_no
AND trunc(prep_date)=trunc(sysdate)
AND prep_status=1
AND prep_error_code IS NULL
ORDER BY prep_date DESC
FETCH FIRST 1 ROW ONLY;
EXIT;
EOF
)

echolog "Fetched BILL_REF_NO=$BILL_REF_NO, BILL_REF_RESETS=$BILL_REF_RESETS, PREP_DATE=$PREP_DATE, STATEMENT_DATE=$STATEMENT_DATE, PAYMENT_DUE_DATE=$PAYMENT_DUE_DATE"


if [[ $? -ne 0 || "$result" == *"ORA-"* ]]; then
  echolog "ERROR: SQL execution failed. Details: $result"
  exit 1
fi

echolog "Inserting new SIN sequence record into SIN_SEQ_NO"
sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
INSERT INTO SIN_SEQ_NO@$db_link
(BILL_REF_NO, BILL_REF_RESETS, OPEN_ITEM_ID, SIN_SEQ_REF_NO, SIN_SEQ_REF_RESETS, FULL_SIN_SEQ, GROUP_ID,
PREP_STATUS, PREP_DATE, STATEMENT_DATE, PAYMENT_DUE_DATE)
VALUES (
$BILL_REF_NO, $BILL_REF_RESETS, 0, $next_sin_seq, 1, '$next_sin_seq', $group_id, 1,
TO_DATE('$PREP_DATE','DD-MON-RR'),
TO_DATE('$STATEMENT_DATE','DD-MON-RR'),
TO_DATE('$PAYMENT_DUE_DATE','DD-MON-RR')
);
COMMIT;
EXIT;
EOF

echolog "Insert completed for FULL_SIN_SEQ=$next_sin_seq and GROUP_ID=$group_id"


if [[ $? -ne 0 ]]; then
  echolog "ERROR: Insert into SIN_SEQ_NO failed."
  exit 1
fi

# Check if the full_sin_seq is present in bill_invoice and sin_seq_no tables
echolog "Checking the full_sin_seq in bill_invoice & sin_seq_no tables"

full_sinseq=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading on feedback on verify off
SELECT s.full_sin_seq
FROM bill_invoice@$db_link b
LEFT JOIN sin_seq_no@$db_link s
ON b.bill_ref_no = s.bill_ref_no
AND b.bill_ref_resets = s.bill_ref_resets
WHERE b.account_no = $account_no
AND s.full_sin_Seq= $next_sin_seq
AND b.prep_date >= TRUNC(SYSDATE);
EXIT;
EOF
)
full_sinseq=$(echo "$full_sinseq" | xargs)
# Error handling
if [ -z "$full_sinseq" ]; then
    echolog "ERROR: Failed to fetch full_sin_seq details or no data found for account_no=$account_no, Please check it in DB, Exiting the script"
    exit 1
else
    echolog "Query executed successfully, Entry is there."
fi

# Estuni STARTER command execution
echolog "Executing ESTUNI STARTER Command"

# Calculate next SIN sequence
sin_seq=$((next_sin_seq - 1))
echolog "$sin_seq"

# Build ESTUNI STARTER command
starter_cmd="/appl_sw/custbill/BIN/STARTER CO\\\$ESTUNI\\\$AP\\\$_\\\$D\\\$${sin_seq}\\\$${next_sin_seq}\\\$1\\\$${group_id}\\\$${statement_date}\\\$1\\\$0\\\$CUST_ID=${server_id}\\\$ID_LANCIO=987654\\\$2\\\$M"

echolog "Command: $starter_cmd"
eval "$starter_cmd"

if [[ $? -ne 0 ]]; then
    echolog "ERROR: STARTER command failed."
    exit 1
else
    echolog "STARTER command executed successfully."
fi

#Checking the status of the ESTUNI Module in CRM_BIL_CON_VIEW_ELAB_BATCH table

echolog "Checking CRM_BIL_CON_VIEW_ELAB_BATCH"

echolog "Waiting for ESTUNI STARTER command to complete..."

while true; do
  CODE_STATO=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 0 VERIFY OFF
SELECT CODE_STATO_BATCH 
FROM CRM_BIL_CON_VIEW_ELAB_BATCH 
WHERE CODE_FUNZION_SIST = 'ESTUNI' 
AND TRUNC(DATA_ORA_INIZIO_ELAB) = TRUNC(SYSDATE)
ORDER BY DATA_ORA_INIZIO_ELAB DESC
FETCH FIRST 1 ROWS ONLY;
EXIT;
EOF
)

  CODE_STATO=$(echo "$CODE_STATO" | xargs)

  if [ "$CODE_STATO" = "SUCC" ]; then
    echolog "ESTUNI STARTER completed successfully. Proceeding..."
    break
  elif [ "$CODE_STATO" = "ERRO" ]; then
    echolog "ESTUNI STARTER failed with ERRO status. Exiting script.Check the log file in /appl_sw/custbill/LOG/FATTURAZIONE/ESTUNI path"
    exit 1
  else
    echolog "ESTUNI STARTER still running or unknown status ('$CODE_STATO'). Waiting..."
    sleep 30  
  fi
done
#check entry is there in crm_bil_post_body table
echolog "check entry is there in crm_bil_post_body table and if entry is there, fetching the full_sin_seq"
full_sin_seq=$(sqlplus -s "${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID}" <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 0 VERIFY OFF
SELECT MAX(full_sin_seq)
FROM crm_bil_post_body
WHERE account_no = '${account_no}'
AND statement_date = TO_DATE('${statement_date}','YYYYMMDD');
EXIT;
EOF
)

# Trim whitespace
full_sin_seq=$(echo "$full_sin_seq" | xargs)

if [ -z "$full_sin_seq" ]; then
  echo "ERROR: full_sin_seq not found for account_no=${account_no} and statement_date=${statement_date}. Exiting."
  exit 1
fi

echo "full_sin_seq found: $full_sin_seq"

# Check entry is there in crm_bil_post_detail table
echolog "check entry is there in crm_bil_post_deatil table"


Amount=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 0 VERIFY OFF
SELECT NVL(SUM(IMPONIBILE), 0)
FROM crm_bil_post_detail
WHERE full_sin_seq = '${full_sin_seq}'
  AND statement_date = TO_DATE('${statement_date}', 'YYYYMMDD');

EXIT;
EOF
)

Amount=$(echo "$Amount" | xargs)

if [[ -z "$Amount" || "$Amount" == "ORA-" || "$Amount" == "SQL*Plus" ]]; then
  echolog "ERROR: Failed to fetch Amount from crm_bil_post_detail"
  exit 1
fi

if [[ -z "$Amount" ]]; then
  echolog "Amount is 0 in crm_bil_post_detail for full_sin_seq=${full_sin_seq} and statement_date=TO_DATE('${statement_date}', 'DDMMYYYY').Check the log file in /appl_sw/custbill/LOG/FATTURAZIONE/ESTUNI path. Exiting the script."
  exit 1
else
  echolog "Rows found in crm_bil_post_detail. Proceeding..."
fi

# Update CRM_BIL_STATUS_MERGER table
sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE
SET FEEDBACK OFF HEADING OFF VERIFY OFF ECHO OFF
UPDATE admincon.CRM_BIL_STATUS_MERGER@coe111
SET num_righe = 0,
    status = 'OK',
    statement_date = TO_DATE('01/01/1960','DD/MM/YYYY');
COMMIT;
EXIT;
EOF

echolog "Updation in CRM_BIL_STATUS_MERGER table completed in admincon DB"
echolog "Checking latest MERGER batch info..."

# Removing the SQL Loader files

cd /appl_sw/custbill/LOG/FATTURAZIONE/MERGER/DEFINITIVO || {
    echo "Directory not found!, Exiting the Script"
    exit 1
}


echo "Listing .SQLLOADER files before deletion:"
ls -l *.SQLLOADER 2>/dev/null

# Remove all .SQLLOADER files
echo "Removing .SQLLOADER files..."
rm -rf *.SQLLOADER

# Check again if any .SQLLOADER files are present
echo "Checking after deletion:"
ls -l *.SQLLOADER 2>/dev/null || echo "No .SQLLOADER files found."

# Fetch latest MERGER batch info
CODE_ID_LANCIO=$(sqlplus -s "${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID}" <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 1 TRIMSPOOL ON LINESIZE 1000

  SELECT CODE_ID_LANCIO
  FROM CRM_BIL_CON_VIEW_ELAB_BATCH
  WHERE CODE_FUNZION_SIST = 'MERGER'
ORDER BY DATA_ORA_INIZIO_ELAB DESC
FETCH FIRST 1 ROWS ONLY;
EXIT;
EOF
)


    new_code_id_lancio=$((CODE_ID_LANCIO + 1))
    echolog "Next CODE_ID_LANCIO: $new_code_id_lancio"
    merger_cmd="/appl_sw/custbill/BIN/STARTER CI\\\$MERGER\\\$AP\\\$_\\\$2\\\$0\\\$CUST_ID=${server_id}\\\$ID_LANCIO=${new_code_id_lancio}\\\$1\\\$M"
    echolog "Executing MERGER STARTER: $merger_cmd"
    eval "$merger_cmd"
if [[ $? -ne 0 ]]; then
    echolog "ERROR:Merger STARTER command failed."
    exit 1
else
    echolog "Merger STARTER command executed successfully."
fi



# Checking the status of the MERGER Module in the CRM_BIL_CON_VIEW_ELAB_BATCH table

echolog "Checking CRM_BIL_CON_VIEW_ELAB_BATCH table"
echolog "Waiting for MERGER STARTER command to complete..."

# Query database for latest status and if it is not, the script should exit
echolog "Fetching the CODE_STATO_BATCH & CODE_USCITA values in CRM_BIL_CON_VIEW_ELAB_BATCH table"

while true; do
RESULT=$(sqlplus -s "${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID}" <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 0 VERIFY OFF
SELECT CODE_STATO_BATCH || '|' || CODE_USCITA
FROM CRM_BIL_CON_VIEW_ELAB_BATCH
WHERE CODE_FUNZION_SIST = 'MERGER'
AND TRUNC(DATA_ORA_INIZIO_ELAB) = TRUNC(SYSDATE)
ORDER BY DATA_ORA_INIZIO_ELAB DESC
FETCH FIRST 1 ROWS ONLY;
EXIT;
EOF
)

    RESULT=$(echo "$RESULT" | xargs)
    CODE_STATO=$(echo "$RESULT" | cut -d'|' -f1)
    CODE_USCITA=$(echo "$RESULT" | cut -d'|' -f2)


if [[ "$CODE_STATO" == "SUCC" ]] || { [[ "$CODE_STATO" == "ERRO" ]] && [[ "$CODE_USCITA" == "40" ]]; }; then
        echolog "MERGER STARTER completed successfully. Proceeding..."
        break
    elif [[ "$CODE_STATO" == "ERRO" ]] && [[ "$CODE_USCITA" != "40" ]]; then
        echolog "MERGER STARTER failed (CODE_STATO='$CODE_STATO', CODE_USCITA='$CODE_USCITA'). Exiting script."
        echolog "Check the log file in /appl_sw/custbill/LOG/FATTURAZIONE/MERGER path"
        exit 1
    else
        echolog "MERGER STARTER still running or unknown status ('$CODE_STATO'). Waiting..."
        sleep 240  
    fi
done


#validation in bb_fatture_incassi table

echolog "Fetching external_id for the account_no=$account_no"
external_id=$(sqlplus -s ${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID} <<EOF
set heading off feedback off verify off
SELECT external_id FROM external_id_acct_map@KCA1 WHERE account_no = '$account_no' AND ROWNUM = 1;
EXIT;
EOF
)

external_id=$(echo "$external_id" | tr -d "[:space:]'")
echolog "Validating entry in bb_fatture_incassi for external_id='$external_id'"

fatture_result=$(sqlplus -s "${USERNAME}/${PASSWORD}@${SID}" <<EOF
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF PAGESIZE 100 TRIMSPOOL ON LINESIZE 1000
SELECT a.external_id, a.account_type, data_scadenza, a.fattura,
       TO_CHAR(a.data_emissione,'DD/MM/YYYY') data_emissione, totale_da_pagare
FROM bb_fatture_incassi a
WHERE external_id =trim('$external_id') and fattura='$full_sin_seq';
EXIT;
EOF
)

if echo "$fatture_result" | grep -q '[[:alnum:]]'; then
    echolog "Entry is present in bb_fatture_incassi for external_id=$external_id and fattura=$full_sin_seq"
else
    echolog "No entry present in bb_fatture_incassi for external_id=$external_id and fattura=$full_sin_seq"
fi

echolog "Checking if External_id exists in crm_bil_post_body_elab table"
external_id=$(echo "$external_id" | tr -d "[:space:]'")
query="SELECT external_id FROM crm_bil_post_body_elab@coe111 WHERE external_id='${external_id}' AND full_sin_seq='${full_sin_seq}';"

ext_id_check=$(sqlplus -s "${INPUT_DB_USER}/${INPUT_DB_PASS}@${INPUT_DB_SID}" <<EOF
WHENEVER SQLERROR EXIT FAILURE
WHENEVER SQLERROR EXIT FAILURE
SET HEADING OFF FEEDBACK OFF VERIFY OFF
${query}
EXIT;
EOF
)
ext_id_check=$(echo "$ext_id_check" | xargs)


if [[ -z "$ext_id_check" || "$ext_id_check" == *"ORA-"* ]]; then
    echolog "ERROR: No entry found for external_id=${external_id}, full_sin_seq=${full_sin_seq}. Check Estuni and Merger execution."
    exit 1
fi

echolog "External_id found in the crm_bil_post_body_elab table"

echolog "Upto Merger action completed.Now text file generation process steps will get start"

/appl_sw/custbill/BIN/Testing/text_file.sh "$account_no" "$external_id" "$full_sin_seq"
