import pandas as pd
import os
import re
import matplotlib.pyplot as plt

# Import aller Protokolle seit September 2017 - Daten sind von hier: https://www.bundestag.de/parlament/plenum/abstimmung/liste
li = []
for filename in sorted(os.listdir(os.getcwd() + "/data/")):
    frame = pd.read_excel("./data/" + filename)
    #Dateiname als Sitzungsdatum
    frame["date"] = pd.to_datetime(re.split("_|-",filename)[0], format = "%Y%m%d")
    li.append(frame)
data = pd.concat(li, axis=0)


data.to_csv("data.csv")

data["date"].max()

#Welche MdBs haben wie oft gefehlt?
MdB = pd.DataFrame(data.groupby(["Fraktion/Gruppe","Bezeichnung"])["nichtabgegeben"].mean())
MdB.sort_values(by ="nichtabgegeben", ascending = False).to_csv("MdBs.csv")

#Nur auf den Zeitraum zwischen den Kontraste Beiträgen bezogen: Welche MdBs und Fraktionen haben wie oft gefehlt?
MdBs_Kontraste = pd.DataFrame(data.loc[(data["date"] >= "2018-10-11") & (data["date"] < "2019-09-26")].groupby(["Fraktion/Gruppe","Bezeichnung"])["nichtabgegeben"].mean())
MdBs_Kontraste.sort_values(by ="nichtabgegeben", ascending = False).to_csv("MdBs_Kontraste.csv")

Fraktionen_Kontraste= pd.DataFrame(data.loc[(data["date"] >= "2018-10-11")  & (data["date"] < "2019-09-26")].groupby("Fraktion/Gruppe")["nichtabgegeben"].mean())
Fraktionen_Kontraste.sort_values(by ="nichtabgegeben", ascending = False).to_csv("Fraktionen_Kontraste.csv")

#Daten vorbereiten, damit wir anständig damit arbeiten können, Floor auf Monatsanfang
data["floordate"] = data["date"] - pd.to_timedelta(data["date"].dt.day - 1, unit='d')

#Frauke Petry interessiert z.B. niemand.
data = data.loc[data["Fraktion/Gruppe"] != "Fraktionslos"]

#
grouped = pd.DataFrame(data.groupby(["Fraktion/Gruppe", "floordate"])["nichtabgegeben"].mean()).reset_index()

#Wir haben 17 Datenpunkte (Monate) für jede Fraktion.
grouped["Fraktion/Gruppe"].value_counts()
#Nicht in allen monaten gibt es namentliche Abstimmungen.
grouped["floordate"].value_counts().sort_index()


#Plotten nach Fraktionen aufgeteilt:
fig, ax = plt.subplots()
grouped.groupby("Fraktion/Gruppe").apply(lambda x: x.plot(x = "floordate", y = "nichtabgegeben", ax=ax, label = x.name))

#Bauen wir noch die richtigen Farben ein:
grouped.groupby("Fraktion/Gruppe").apply(lambda x: print(x.name))
col = ["blue", "green", "black", "pink", "yellow", "red"]
for i, axis in enumerate(ax.get_lines()):
    print(axis.get_label())
    ax.get_legend().legendHandles[i].set_color(col[i])
    axis.set_color(col[i])

#Noch zwei Linien für die Beiträge
ax.axvline(x = "2018-10-11", color = "r")
ax.text("2018-10-25",0.15,'Kontraste Beitrag',rotation=90, color = "red")

ax.axvline(x = "2019-09-26", color = "r")
ax.text("2019-10-10",0.15,'Kontraste Beitrag',rotation=90, color = "red")

#Bisschen Abstand, damit die zweite Linie reinpasst:
ax.set_xlim(right = "2019-10-31")

#Fertig ist das Mondgesicht: 
fig.savefig("plots/plot.png")
