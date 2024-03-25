import pandas as pd

def getData(name):
    df = pd.read_csv('A_Z_medicines_dataset_of_India.csv')
    content = df[['name','short_composition1']].loc[df['name'].str.contains(name, case=False)].iloc[0]['short_composition1']
    data = df[['name','price(₹)']].loc[df['short_composition1'] == content]
    names = data['name'].values.tolist()
    prices = data['price(₹)'].values.tolist()
    data = [{"name": names[i], "price": prices[i]} for i in range(len(names))][:11]
    return data