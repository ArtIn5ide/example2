from datetime import datetime
from time import sleep
import schedule

import requests

from constants import FULL_TICKBOX, HEADERS, PARAMS, PROJ_URL, SUCCESS


description_changed = True


def un_complete():
    """Makes GET request to the Gitlab project issues, changes their description
    and PUTs it back.
    """
    global description_changed

    # GET checklist contents, aka issue description
    try:
        requests.get(PROJ_URL, headers=HEADERS, params=PARAMS)
    except:
        description_changed = False
    else:
        r = requests.get(PROJ_URL, headers=HEADERS, params=PARAMS)

    # if transaction was a success, i.e. response has our info
    if r.status_code == SUCCESS:
        for checklist in r.json():
            # Switch filled checkboxes to empty ones
            description = checklist["description"].replace("\\n", "\n")
            description = FULL_TICKBOX.sub("* [ ]", description)
            # PUT new description to corresponding issue
            try:
                requests.put(
                    f"{PROJ_URL}/{checklist['iid']}",
                    headers=HEADERS,
                    params={"description": description},
                )
            except:
                description_changed = False

        description_changed = True
    else:
        description_changed = False


labels_changed = True


def rm_labels():
    """Makes GET request to the Gitlab project issues and removes all assigned labels."""
    global labels_changed

    # GET labels contents, aka issue labels
    try:
        requests.get(PROJ_URL, headers=HEADERS, params=PARAMS)
    except:
        labels_changed = False
    else:
        r = requests.get(PROJ_URL, headers=HEADERS, params=PARAMS)

    if r.status_code == SUCCESS:
        for issue in r.json():
            try:
                requests.put(
                    f"{PROJ_URL}/{issue['iid']}/?labels",
                    headers=HEADERS,
                    params={"labels": []},
                )
            except:
                labels_changed = False
        labels_changed = True
    else:
        labels_changed = False


if __name__ == "__main__":
    func = rm_labels
    job = schedule.every().day.at("00:00").do(func).tag("EST_checklist")

    while True:
        # Attempt to uncheck everything
        schedule.run_pending()
        # if request didn't make it we run the job every second until we succeed
        while not labels_changed:
            job.run()
            sleep(1)
        sleep(1)
