import pandas as pd

from pixfraud.external import (
    PIX_LIKE_FORMATS,
    load_amlworld,
    load_amlworld_patterns,
    load_paysim,
    pattern_accounts,
    time_windows,
)
from pixfraud.graph import build_graph

AMLWORLD = """Timestamp,From Bank,Account,To Bank,Account,Amount Received,Receiving Currency,Amount Paid,Payment Currency,Payment Format,Is Laundering
2022/09/01 00:20,10,8000EBD30,10,8000EBD30,3697.34,US Dollar,3697.34,US Dollar,Reinvestment,0
2022/09/01 00:20,3208,8000F4580,1,8000F5340,0.01,US Dollar,0.01,US Dollar,Cheque,0
2022/09/01 00:00,3209,8000F4670,3209,8000F4670,14675.57,US Dollar,14675.57,US Dollar,Reinvestment,0
2022/09/01 00:02,12,8000F5030,12,8000F5030,2806.97,US Dollar,2806.97,US Dollar,Reinvestment,0
2022/09/01 00:06,10,8000F5200,10,8000F5200,36682.97,US Dollar,36682.97,US Dollar,Reinvestment,0
2022/09/01 00:03,1,8000F5340,1,8000F5340,0.01,US Dollar,0.01,US Dollar,Credit Card,0
2022/09/02 10:00,70,100428660,1124,800825340,389769.39,US Dollar,389769.39,US Dollar,Cash,1
2022/09/02 11:00,1124,800825340,1124,800825341,1000.00,Euro,1000.00,Euro,ACH,1
2022/09/03 12:00,1,8000F5340,70,100428660,50.00,US Dollar,50.00,US Dollar,ACH,0
"""

PATTERNS = """BEGIN LAUNDERING ATTEMPT - FAN-OUT:  Max 2-degree Fan-Out
2022/09/01 05:14,00952,8139F54E0,021174,800737690,2848.96,US Dollar,2848.96,US Dollar,ACH,1
2022/09/01 07:00,00952,8139F54E0,01,8000F5340,1000.00,US Dollar,1000.00,US Dollar,ACH,1
END LAUNDERING ATTEMPT - FAN-OUT

BEGIN LAUNDERING ATTEMPT - CYCLE:  Max 3 hops
2022/09/02 10:00,070,100428660,01124,800825340,389769.39,US Dollar,389769.39,US Dollar,Cash,1
2022/09/02 11:00,01124,800825340,070,100428660,1000.00,US Dollar,1000.00,US Dollar,ACH,1
END LAUNDERING ATTEMPT - CYCLE
"""

PAYSIM = """step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud,isFlaggedFraud
1,PAYMENT,9839.64,C1231006815,170136.0,160296.36,M1979787155,0.0,0.0,0,0
1,TRANSFER,181.0,C1305486145,181.0,0.0,C553264065,0.0,0.0,1,0
1,CASH_OUT,181.0,C840083671,181.0,0.0,C38997010,21182.0,0.0,1,0
2,TRANSFER,500.0,C1231006815,160296.36,159796.36,C553264065,181.0,681.0,0,0
"""


def test_load_amlworld(tmp_path):
    path = tmp_path / "HI-Small_Trans.csv"
    path.write_text(AMLWORLD, encoding="utf-8")
    accounts, tx = load_amlworld(path)
    assert len(tx) == 3  # sem autotransferências e sem a linha em euro
    assert set(tx["sender"]) == {"3208_8000F4580", "70_100428660", "1_8000F5340"}
    assert tx["is_fraud"].sum() == 1 and tx.loc[tx["is_fraud"], "scenario"].item() == "lavagem"
    fraud = set(accounts.loc[accounts["is_fraud"], "account_id"])
    assert fraud == {"70_100428660", "1124_800825340"}
    assert list(accounts.columns) == ["account_id", "account_type", "account_age_days", "role", "is_fraud", "is_victim"]
    assert build_graph(tx, accounts["account_id"]).number_of_nodes() == len(accounts)
    assert len(load_amlworld(path, currency=None)[1]) == 4
    assert len(load_amlworld(path, days=1)[1]) == 1


def test_load_paysim(tmp_path):
    path = tmp_path / "paysim.csv"
    path.write_text(PAYSIM, encoding="utf-8")
    accounts, tx = load_paysim(path)
    info = accounts.set_index("account_id")
    assert info.loc["C553264065", "is_fraud"] and info.loc["C38997010", "is_fraud"]
    assert info.loc["C1305486145", "is_victim"] and not info.loc["C1305486145", "is_fraud"]
    assert tx["timestamp"].iloc[-1].hour == 2


def test_amlworld_payment_formats(tmp_path):
    path = tmp_path / "HI-Small_Trans.csv"
    path.write_text(AMLWORLD, encoding="utf-8")
    _, all_formats = load_amlworld(path)
    _, pix_like = load_amlworld(path, formats=PIX_LIKE_FORMATS)
    assert len(all_formats) == 3 and len(pix_like) == 1  # sobra só o ACH em dólar
    assert pix_like["sender"].item() == "1_8000F5340"


def test_load_amlworld_patterns(tmp_path):
    path = tmp_path / "HI-Small_Patterns.txt"
    path.write_text(PATTERNS, encoding="utf-8")
    patterns = load_amlworld_patterns(path)
    assert patterns["attempt"].tolist() == [1, 1, 2, 2]
    assert patterns["typology"].tolist() == ["fan_out", "fan_out", "cycle", "cycle"]
    # zeros à esquerda no código do banco são removidos, como no *_Trans.csv
    assert patterns["sender"].iloc[0] == "952_8139F54E0" and patterns["receiver"].iloc[1] == "1_8000F5340"
    assert patterns["amount"].iloc[0] == 2848.96
    members = pattern_accounts(patterns)
    assert set(members.loc[members["typology"] == "cycle", "account_id"]) == {"70_100428660", "1124_800825340"}
    assert len(members) == 5


def test_time_windows_relabel_each_window():
    tx = pd.DataFrame({
        "tx_id": ["T1", "T2", "T3"],
        "timestamp": pd.to_datetime(["2022-09-01 10:00", "2022-09-02 10:00", "2022-09-04 09:00"]),
        "sender": ["a", "b", "a"],
        "receiver": ["b", "c", "d"],
        "amount": [10.0, 20.0, 30.0],
        "is_fraud": [False, False, True],
        "scenario": ["ACH", "ACH", "lavagem"],
    })
    windows = list(time_windows(tx, days=2))
    assert [start.day for start, _, _ in windows] == [1, 3]
    _, first_accounts, first_tx = windows[0]
    assert len(first_tx) == 2 and not first_accounts["is_fraud"].any()
    _, second_accounts, _ = windows[1]
    assert set(second_accounts.loc[second_accounts["is_fraud"], "account_id"]) == {"a", "d"}
