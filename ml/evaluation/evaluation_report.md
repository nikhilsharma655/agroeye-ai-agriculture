# AgroEye ML Evaluation Report


## Crop Recommendation (Classification)

**Selected model:** `random_forest`


| Model | Metrics |
|---|---|
| random_forest | accuracy=0.9857, precision=0.9864, recall=0.9857, f1_score=0.9857 |
| gradient_boosting | accuracy=0.9810, precision=0.9816, recall=0.9810, f1_score=0.9810 |
| logistic_regression | accuracy=0.9738, precision=0.9748, recall=0.9738, f1_score=0.9736 |

## Yield Prediction (Regression)

**Selected model:** `gradient_boosting`


| Model | Metrics |
|---|---|
| random_forest | mae=0.7684, mse=3.1186, rmse=1.7659, r2=0.9882 |
| gradient_boosting | mae=0.8114, mse=2.6455, rmse=1.6265, r2=0.9900 |
| linear_regression | mae=0.7798, mse=3.4442, rmse=1.8559, r2=0.9869 |

## Disease Risk (Classification)

**Selected model:** `gradient_boosting`


| Model | Metrics |
|---|---|
| random_forest | accuracy=0.7841, precision=0.8001, recall=0.7841, f1_score=0.7758 |
| gradient_boosting | accuracy=0.7977, precision=0.8043, recall=0.7977, f1_score=0.7926 |