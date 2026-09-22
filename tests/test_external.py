from pixfraud.external import load_amlworld, load_paysim
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
