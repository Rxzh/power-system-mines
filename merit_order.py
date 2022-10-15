import matplotlib.pyplot as plt
import pandas as pd

class MeritOrder(object):

    def __init__(self, dict_pmax, dict_price, demand):
        '''
        Args:
        --------
            - dict_pmax : key = "solar", "gas", "coal" etc and
            value is the maw power available by source in MW
            - dict_price : key = "solar", "gas", "coal" etc and
            the values are the price of the MW with this source
            - self.demand : the current consumption in MW
        '''

        self.dict_pmax = dict_pmax
        self.dict_price = dict_price
        self.demand = demand

    def compute_electricity_price(self):

        production = 0
        dict_price = self.dict_price.copy()

        while production < self.demand:
            source = min(dict_price, key=dict_price.get)
            production += self.dict_pmax[source]
            dict_price.pop(source)


        return source, self.dict_price[source]

    def _get_df(self):

        df = pd.DataFrame.from_dict(data=self.dict_pmax, orient='index', columns=["Available capacity (MW)"])
        df["Marginal Costs"] = df.index.map(self.dict_price)
        df = df.sort_values(by="Marginal Costs")
        df["Cumulative Capacity (MW)"] = df["Available capacity (MW)"].cumsum()

        # position of the block on the plot
        df["xpos"] = df["Cumulative Capacity (MW)"].shift(1).fillna(0) + df["Available capacity (MW)"] / 2
        return df

    def plot(self):

        plt.figure(figsize = (20, 12))
        plt.rcParams["font.size"] = 16

        df = self._get_df()

        power_plants = dict(sorted(self.dict_price.items(), key=lambda item: item[1]))
        power_plants = list(power_plants.keys())
        # power_plants = list(self.dict_pmax.keys())

        colors = [
            "yellow",
            "limegreen",
            "skyblue",
            "pink",
            "limegreen",
            "black",
            "orange",
            "grey",
            "maroon"
        ]
        
        xpos = df["xpos"].values.tolist()
        y = df["Marginal Costs"].values.tolist()
        w = df["Available capacity (MW)"].values.tolist()
        (cut_off_power_plant, price) = self.compute_electricity_price()

        fig = plt.bar(xpos, 
                height = y,
                width = w,
                fill = True,
                color = colors)

        plt.xlim(0, df["Available capacity (MW)"].sum())
        plt.ylim(0, df["Marginal Costs"].max() + 20)

        plt.hlines(y = df.loc[cut_off_power_plant, "Marginal Costs"],
                xmin = 0,
                xmax = self.demand,
                color = "red",
                linestyle = "dashed")

        plt.vlines(x = self.demand,
                ymin = 0,
                ymax = df.loc[cut_off_power_plant, "Marginal Costs"],
                color = "red",
                linestyle = "dashed",
                label = "self.demand")

        plt.legend(fig.patches, power_plants,
                loc = "best",
                ncol = 3)

        plt.text(x = self.demand - df.loc[cut_off_power_plant, "Available capacity (MW)"]/2,
                y = df.loc[cut_off_power_plant, "Marginal Costs"] + 10,
                s = f"Electricity price: \n    {df.loc[cut_off_power_plant, 'Marginal Costs']} $/MWh")

        plt.xlabel("Power plant capacity (MW)")
        plt.ylabel("Marginal Cost ($/MWh)")
        plt.show()

