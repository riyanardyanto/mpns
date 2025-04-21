import asyncio
import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs

from src.gui.toast import create_toast
from src.utils.constants import HEADERS, NTLM_AUTH
from src.utils.csvhandle import load_targets_df


async def fetch_data(url: str, client: httpx.AsyncClient):
    try:
        response = await client.get(url, headers=HEADERS, auth=NTLM_AUTH)
        if response.status_code == 200:
            soup = bs(response.text, features="lxml")
            elements = soup.find_all("td")
            actual = {
                "PR": elements[
                    elements.index(soup.find("td", string="Strat. PR=")) + 1
                ].text,
                "MTBF": elements[
                    elements.index(soup.find("td", string="Strat. PR=")) + 3
                ].text,
                "NATR": elements[
                    elements.index(soup.find("td", string="Not at Target Rate")) + 3
                ].text,
                "PDT": elements[
                    elements.index(soup.find("td", string="Planned downtime")) + 4
                ].text,
                "STOP": elements[
                    elements.index(soup.find("td", string="Unplanned downtime")) + 1
                ].text,
                "UPDT": elements[
                    elements.index(soup.find("td", string="Unplanned downtime")) + 4
                ].text,
            }
            return actual
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
