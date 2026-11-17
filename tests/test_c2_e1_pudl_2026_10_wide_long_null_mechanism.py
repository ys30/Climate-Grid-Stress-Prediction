"""C-2 E1: version-pinned PUDL EIA861 wide-to-long null-row mechanism regression.

This synthetic micro-example demonstrates *possibility*, NOT proof that every
original 1,321 PUDL null row was synthesized. No hourly demand or model fitting.
"""
import unittest

class TestTaggedPUDLWideToLongNullMechanism(unittest.TestCase):
    def test_pandas_stack_dropna_false_creates_null_sector_rows(self):
        import pandas as pd
        # One raw wide EIA861-like filing with actual residential sales only.
        wide=pd.DataFrame({
            "utility_id_eia":[123],
            "residential_sales_mwh":[100.0],
            "residential_customers":[10.0],
            "other_sales_mwh":[float("nan")],
            "other_customers":[float("nan")],
        }).set_index("utility_id_eia")
        values=wide.copy()
        values.columns=values.columns.str.split(
            r"(?<=residential)_(?=sales|customers)|(?<=other)_(?=sales|customers)",
            n=1,expand=True)
        # PUDL v2026.10.0 was written for the legacy pandas stack API.
        # pandas >=3 removed dropna=False, so demonstrate the same preserved
        # all-null sector row using an explicit NA-preserving long conversion.
        if int(pd.__version__.split(".")[0]) < 3:
            long=values.stack(level=0,dropna=False)
        else:
            long=(values.stack(level=0)
                  .reindex(pd.MultiIndex.from_product(
                      [values.index,["other","residential"]],
                      names=[values.index.name,values.columns.names[0]])))
        # Historical PUDL v2026.10.0 _tidy_class_dfs uses stack(level=0, dropna=False).
        self.assertEqual(len(long),2)
        self.assertEqual(long.loc[(123,"residential"),"sales_mwh"],100.0)
        self.assertTrue(pd.isna(long.loc[(123,"other"),"sales_mwh"]))
        self.assertTrue(pd.isna(long.loc[(123,"other"),"customers"]))
        # A row's presence alone does not certify reported electric sales.

if __name__=="__main__":unittest.main()
