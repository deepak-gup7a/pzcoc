
import pandas as pd


from utils import *
from nasnas import NASNAS
from CONSTANTS import TOP_N


data = pd.read_csv('DATASETS/small.csv')
x = data.drop('label', axis=1, inplace=False).values
y = pd.get_dummies(data['label']).values

print(y)
nas_object = NASNAS(x, y)
data = nas_object.search()

get_top_n_architectures(TOP_N)
