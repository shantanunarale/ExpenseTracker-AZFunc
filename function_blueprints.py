import azure.functions as func
import logging
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

bp = func.Blueprint()


@bp.function_name(name="fn_logExpenseEvents")
@bp.route(route="logexpenseevents", auth_level=func.AuthLevel.FUNCTION, methods=[func.HttpMethod.GET, func.HttpMethod.POST])
@bp.table_output(arg_name="expbody", connection="ExpenseTrackerTableStorage", table_name="%ExpenseTableName%")
def fn_logExpenseEvents(req: func.HttpRequest, expbody: func.Out[str]):
    if req.method == "GET":
        response_body = """This function endpoint is used for logging Expense events. The sample request format is
        
        {
            \"Category\":\"<<Expense Category>>\",
            \"PaymentMethod\":\"<<Payment Method>>\",
            \"Bank\":\"<<Bank>>\",
            \"Amount\":\"<<Amount>>\",
            \"Expense\":\"<<Expense>>\"
        }
        """
        logging.debug("Received GET request.")
        return func.HttpResponse(body=response_body, status_code=200)
    if req.method == "POST":
        payload = req.get_json()
        today = datetime.now(tz=ZoneInfo('UTC'))
        today = today.astimezone(tz=ZoneInfo("Asia/Calcutta"))
        payload["PartitionKey"] = today.strftime("%B-%Y")
        payload["RowKey"] = today.strftime("%d") + "-" + str(uuid.uuid4())
        if "Payment Method" in payload.keys():
            payment_method = payload.pop("Payment Method")
            payload["PaymentMethod"] = payment_method
        resp_body = ""
        resp_code = 500
        try:
            payload["Amount"] = float(payload["Amount"])
            expbody.set(json.dumps(payload))
            logging.debug(
                f"Row inserted with Partition Key {payload['PartitionKey']} and Row Key {payload['RowKey']}.")
            resp_body = "Success"
            resp_code = 200
        except:
            logging.error(f"Unable to insert - {json.dumps(payload)}")
            resp_body = "Failure - Unable to insert in Table Storage."
            resp_code = 500
        finally:
            return func.HttpResponse(body=resp_body, status_code=resp_code)
