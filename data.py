import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests


API_KEY = "NL04VP2IPHMIWGSI"
FED_INTEREST_RATES = "data/FEDFUNDS.csv"  # https://fred.stlouisfed.org/series/FEDFUNDS


def get_stock_data(ticker: str):
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={API_KEY}"
  r = requests.get(url)
  data = r.json()

  row_data = []
  time_series = data["Time Series (Daily)"]
  for date, stock_data in time_series.items():
    open_price, close_price = float(stock_data["1. open"]), float(stock_data["4. close"])
    low_price, high_price = float(stock_data["3. low"]), float(stock_data["2. high"])
    row_data.append((date, close_price))

  df = pd.DataFrame(row_data, columns=("date", ticker))
  df["date"] = pd.to_datetime(df.date)
  return df


def merge_data(df1: pd.DataFrame, df2: pd.DataFrame):
  common_start_date = max(df1.date.min(), df2.date.min())
  df1 = df1[df1.date >= common_start_date]
  df2 = df2[df2.date >= common_start_date]
  return pd.merge(df1, df2.dropna(subset=['date']), how='outer', on='date')


def plot(df: pd.DataFrame):
  # fig = px.line(
  #   df, x="date", y=df.columns,
  #   # hover_data={"date": "|%B %d, %Y"},
  #   title=f"{df.columns}"
  # )
  fig = go.Figure()

  df = df.set_index("date")
  for idx, column in enumerate(df.columns):
    trace_df = df.dropna(subset=[column])
    fig.add_trace(
        go.Scatter(x=trace_df.index, y=trace_df[column], name=column, yaxis=f"y{idx+1}")
    )

  # Add figure title
  fig.update_layout(
      title_text=f"{list(df.columns)}"
  )

  # Set x-axis title
  fig.update_xaxes(
    title_text="Date",
    dtick="M1",
    tickformat="%b\n%Y"
  )

  fig.update_layout(
    {
      f"yaxis{'' if idx==0 else idx+1}": {
          "position": 1 - (idx / 20),
          "overlaying": None if idx==0 else "y",
          # "side": "left" if idx % 2 == 0 else "right"
      }
      for idx in range(len(df.columns))
    }
  )
  fig.update_traces(connectgaps=True)
  return fig


def get_fed_funds() -> pd.DataFrame:
  fed_funds = pd.read_csv(FED_INTEREST_RATES).rename(columns={"DATE": "date", "FEDFUNDS": "rate"})
  fed_funds["date"] = pd.to_datetime(fed_funds.date)
  return fed_funds


data = get_stock_data("ALLY")
fed_funds = get_fed_funds()
df = merge_data(data, fed_funds)
plot(df).show()
