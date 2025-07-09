import asyncio

import httpx
import numpy as np
import pandas as pd
import spa_scraper_pyo3

from src.gui.toast import create_toast
from src.utils.constants import HEADERS, NTLM_AUTH
from src.utils.csvhandle import load_targets_df


async def fetch_data(url: str, client: httpx.AsyncClient):
    try:
        response = await client.get(url, headers=HEADERS, auth=NTLM_AUTH)
        if response.status_code == 200:
            data = spa_scraper_pyo3.extract_loss_tree(response.text)

            time_period = data.time_range.calendar_time

            actual = {
                "PR": data.time_range.pr,
                "MTBF": data.time_range.mtbf,
                "NATR": data.rate_loss.natr.uptime_loss,
                "PDT": data.planned.pdt.uptime_loss,
                "STOP": data.unplanned.updt.stops,
                "UPDT": data.unplanned.updt.uptime_loss,
            }
            return actual, time_period
        else:
            create_toast(f"HTTP Error: Status {response.status_code}", "danger")
            return None
    except Exception as e:
        create_toast(f"Error fetching data: {e}", "danger")
        return None


async def post_data(url: str, client: httpx.AsyncClient, parameter: str):
    try:
        response = await client.post(
            url + "&" + parameter, headers=HEADERS, auth=NTLM_AUTH
        )
        if response.status_code == 200:
            data = spa_scraper_pyo3.extract_loss_tree(response.text)

            time_period = data.time_range.calendar_time

            actual = {
                "PR": data.time_range.pr,
                "MTBF": data.time_range.mtbf,
                "NATR": data.rate_loss.natr.uptime_loss,
                "PDT": data.planned.pdt.uptime_loss,
                "STOP": data.unplanned.updt.stops,
                "UPDT": data.unplanned.updt.uptime_loss,
            }
            return actual, time_period
        else:
            create_toast(f"HTTP Error: Status {response.status_code}", "danger")
            return None
    except Exception as e:
        create_toast(f"Error fetching data: {e}", "danger")
        return None


async def read_csv(file_path: str, shift=1):
    try:
        # pandas bukan async, jadi kita jalankan di executor untuk I/O-bound task
        loop = asyncio.get_event_loop()
        df = await loop.run_in_executor(None, load_targets_df, file_path)

        # df = df[
        #     f"{datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%a')}_{shift}"
        # ]
        df = df[f"Shift {shift}"]
        list_target = df.astype(str).str.replace("%", "").values
        return dict(zip(["STOP", "PR", "MTBF", "UPDT", "PDT", "NATR"], list_target))

    except Exception as e:
        create_toast(f"Error reading Excel: {e}", "danger")
        return None


def get_time_period(response: httpx.Response):
    # df = pd.read_html(response.content)
    data = spa_scraper_pyo3.extract_stop_stats(response.text)
    time_period = data.time_period
    return time_period
    # return str(df[3][1][2])


def extract_dataframe(response: httpx.Response):
    df = pd.read_html(response.content)

    pos = []
    equipment = []

    for i in range(len(df)):
        if "ID01" in str(df[i][0][0]):
            pos.append(i)
            equipment.append(df[i][0][0])

    df_name_list = []
    for i in range(len(equipment)):
        df_name = f"df_{str(equipment[i][-4:]).lower()}"
        df_name_list.append(df_name)

    for i in range(len(equipment)):
        machine_name = df[pos[i]][[2]].values[1][0]
        dfHeader = list(df[pos[i] + 1].iloc[0])
        dfHeader[-1] = "Machine"
        n_df = pd.DataFrame(df[pos[i] + 1])
        n_df.columns = dfHeader

        new_df = n_df["Machine"]
        new_df.replace(np.nan, machine_name, inplace=True)
        n_df["Machine"] = new_df

        df_name_list[i] = n_df[1:]

    concatenated = pd.concat(df_name_list).reset_index().drop(labels=["index"], axis=1)
    convert_st = concatenated["Stops"].apply(pd.to_numeric).values.tolist()
    convert_dt = concatenated["DT [min]"].apply(pd.to_numeric).values.tolist()

    final_df = concatenated[["Machine", "Description", "Stops", "DT [min]"]]

    final_df.loc[:, "Stops"] = convert_st
    final_df.loc[:, "DT [min]"] = convert_dt

    return final_df
    # return final_df.to_dict(orient="records")


def get_data_spa(response: httpx.Response):
    stop_stats = spa_scraper_pyo3.extract_stop_stats(response.text)

    data = [
        [
            machine.machine_type.split("-")[1],
            stop_reason.description,
            int(stop_reason.stops),
            float(stop_reason.downtime_min),
        ]
        for machine in stop_stats.machines
        for stop_reason in machine.stop_reasons
    ]

    return pd.DataFrame(data, columns=["Machine", "Description", "Stops", "DT [min]"])
