# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 10:16:38 2018

@author: dgill
"""

_DEBUG = True
DATA_DIR = 'D:\\School\\Machine Learning\\fnma_loan_performance\\data\\landing'
DIW_DIR = 'D:\\School\Machine Learning\\fnma_loan_performance\\data\\diw'
CATEGORY_MAPPING_DIR = 'D:\\School\Machine Learning\\fnma_loan_performance\\output\\category_mappings'
FEATURE_SELECTION_DIR = 'D:\\School\Machine Learning\\fnma_loan_performance\\output\\feature_selection'
PACKAGE_PATH = 'D:\\School\\Machine Learning\\fnma_loan_performance\\packages'
# All of the headers in the two files
HEADERS = {
    "Acquisition": [
        "id",
        "channel",
        "seller",
        "interest_rate",
        "balance",
        "loan_term",
        "origination_date",
        "first_payment_date",
        "ltv",
        "cltv",
        "borrower_count",
        "dti",
        "borrower_credit_score",
        "first_time_homebuyer",
        "loan_purpose",
        "property_type",
        "unit_count",
        "occupancy_status",
        "property_state",
        "zip",
        "insurance_percentage",
        "product_type",
        "co_borrower_credit_score",
        "mortgage_insurance_type",
        "relocation_mortgage_indicator"
    ],
    "Performance": [
        "id",
        "reporting_period",
        "servicer_name",
        "interest_rate",
        "balance",
        "loan_age",
        "months_to_maturity",
        "adj_months_to_maturity",
        "maturity_date",
        "msa",
        "delinquency_status",
        "modification_flag",
        "zero_balance_code",
        "zero_balance_date",
        "last_paid_installment_date",
        "foreclosure_date",
        "disposition_date",
        "foreclosure_costs",
        "property_repair_costs",
        "recovery_costs",
        "misc_costs",
        "tax_costs",
        "sale_proceeds",
        "credit_enhancement_proceeds",
        "repurchase_proceeds",
        "other_foreclosure_proceeds",
        "non_interest_bearing_balance",
        "principal_forgiveness_balance",
        "repurchase_flag",
        "foreclocure_principal_writeoff_amt",
        "servicing_activity_indicator"
    ]
}
# The select list consists of the columns we wish to keep
SELECT = {
    "Acquisition": HEADERS["Acquisition"],
    "Performance": [
        "id",
        "foreclosure_date"
    ]
}
TARGET = 'foreclosure_status'
DROP_COLS = [
    'origination_date'
    ,'first_payment_date'
    ,'co_borrower_credit_score'
    ,'mortgage_insurance_type'
    ,'insurance_percentage'
    ,'relocation_mortgage_indicator'
    ,'product_type'        
]
# TODO: reduce the predictor count
NON_PRED = [TARGET, "id"]
FOLDS = 3
# Minimum # of quarters a loan must be in the dataset for inclusion
MINIMUM_QUARTER_COUNT = 4
DROP_DATA_AFTER_TRAINING = False
DYNAMIC_FEATURE_SELECTION = False
CONFIG_DIR = 'config'
CONFIG_FILE = 'app.conf'
