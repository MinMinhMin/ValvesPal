import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import requests
import datetime
from typing import Dict, List, Union
from collections import defaultdict


# Class GameDealFetcher để lấy dữ liệu từ API
class GameDealFetcher:
    def __init__(
        self,
        api_key: str,
        game_id: str,
        shops_file: str,
        country: str = "US",
        shops: str = "61,35,16,6,20,24,37",
        since: str = "2023-11-06T00:00:00Z",
    ):
        self.api_key = api_key
        self.base_url = "https://api.isthereanydeal.com/games/history/v2"
        self.params = {
            "key": self.api_key,
            "id": game_id,
            "country": country,
            "shops": shops,
            "since": since,
        }
        self.shops_data = self.load_shops_data(shops_file)

    def load_shops_data(self, shops_file: str) -> Dict:
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file shops JSON: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        formatted_data = []

        for item in data:
            shop_id = str(item["shop"]["id"])
            shop_name = self.shops_data.get(shop_id, "Unknown Shop")
            timestamp = item["timestamp"]
            deal_info = {
                "timestamp": timestamp,
                "price": item["deal"]["price"]["amount"],
                "regular_price": item["deal"]["regular"]["amount"],
                "cut": item["deal"]["cut"],
            }

            shop_entry = next(
                (s for s in formatted_data if s["shop_id"] == shop_id), None
            )

            if not shop_entry:
                shop_entry = {"shop_id": shop_id, "shop_title": shop_name, "deals": []}
                formatted_data.append(shop_entry)

            shop_entry["deals"].append(deal_info)

        return formatted_data


# Class DiscountFrequencyHeatmap để tạo biểu đồ Heatmap
class DiscountFrequencyHeatmap:
    def __init__(self, shops_data: List[Dict]):
        self.shops_data = shops_data

    def process_raw_data(self) -> Dict:
        discount_frequency = defaultdict(lambda: defaultdict(int))
        for shop in self.shops_data:
            shop_title = shop["shop_title"]

            for deal in shop["deals"]:
                date = datetime.datetime.fromisoformat(deal["timestamp"]).strftime(
                    "%Y-%m"
                )
                discount = deal["cut"]
                discount_frequency[(shop_title, date)][discount] += 1

        heatmap_data = []
        shop_titles = sorted({shop["shop_title"] for shop in self.shops_data})
        dates = sorted({date for (_, date) in discount_frequency.keys()})

        for i, shop in enumerate(shop_titles):
            for j, date in enumerate(dates):
                total_frequency = sum(discount_frequency[(shop, date)].values())
                heatmap_data.append([i, j, total_frequency])

        return {
            "shop_titles": shop_titles,
            "dates": dates,
            "heatmap_data": heatmap_data,
            "discount_frequency": discount_frequency,
        }

    def predict_next_three_months(
        self, discount_frequency: defaultdict, last_date: str
    ) -> List[List[int]]:
        shop_titles = sorted({shop["shop_title"] for shop in self.shops_data})
        dates = pd.to_datetime(
            sorted({date for (_, date) in discount_frequency.keys()})
        )

        next_three_months = []
        last_month = pd.to_datetime(last_date)

        for i in range(1, 4):
            next_month = (last_month + pd.DateOffset(months=i)).strftime("%Y-%m")
            next_three_months.append(next_month)

        predictions = []
        for i, shop in enumerate(shop_titles):
            shop_data = [
                sum(discount_frequency[(shop, date.strftime("%Y-%m"))].values())
                for date in dates
            ]
            if len(shop_data) > 1:
                x = np.arange(len(shop_data)).reshape(-1, 1)
                y = np.array(shop_data)
                model = LinearRegression().fit(x, y)
                future_x = np.arange(len(shop_data), len(shop_data) + 3).reshape(-1, 1)
                predicted_values = model.predict(future_x)
                predictions.extend(
                    [
                        [i, len(dates) + j, max(0, int(pred))]
                        for j, pred in enumerate(predicted_values)
                    ]
                )
            else:
                predictions.extend([[i, len(dates) + j, 0] for j in range(3)])

        return predictions, next_three_months

    def generate_chart_config(self):
        processed_data = self.process_raw_data()
        shop_titles = processed_data["shop_titles"]
        dates = processed_data["dates"]
        heatmap_data = processed_data["heatmap_data"]

        prediction_data, next_three_months = self.predict_next_three_months(
            processed_data["discount_frequency"], dates[-1]
        )
        extended_dates = dates + next_three_months
        prediction_heatmap_data = prediction_data

        original_chart_config = {
            "chart": {
                "type": "heatmap",
                "plotBorderWidth": 1,
                "zoomType": "xy",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "title": {
                "text": "Discount Frequency Analysis for Each Shop",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "xAxis": {
                "categories": shop_titles,
                "title": {
                    "text": "Shops",
                },
                "labels": {"style": {"fontSize": "10px"}},
            },
            "yAxis": {
                "categories": extended_dates,
                "title": {"text": "Month"},
                "reversed": True,
                "labels": {"style": {"fontSize": "10px"}},
            },
            "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"},
            "legend": {
                "align": "right",
                "layout": "vertical",
                "margin": 0,
                "verticalAlign": "top",
                "y": 25,
                "symbolHeight": 280,
            },
            "tooltip": {"pointFormat": "Discount Frequency: <b>{point.value}</b>"},
            "series": [
                {
                    "name": "Discount Frequency",
                    "borderWidth": 1,
                    "data": heatmap_data,
                    "dataLabels": {
                        "enabled": True,
                        "color": "#000000",
                        "format": "{point.value}",
                    },
                }
            ],
        }

        prediction_chart_config = {
            "chart": {
                "type": "heatmap",
                "plotBorderWidth": 1,
                "zoomType": "xy",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "title": {
                "text": "Predicted Discount Frequency for Next Three Months",
                "style": {"fontFamily": "MyCustomFont"},
            },
            "xAxis": {
                "categories": shop_titles,
                "title": {"text": "Shops"},
                "labels": {"style": {"fontSize": "10px"}},
            },
            "yAxis": {
                "categories": extended_dates,
                "title": {"text": "Month"},
                "reversed": True,
                "labels": {"style": {"fontSize": "10px"}},
            },
            "colorAxis": {"min": 0, "minColor": "#FFFFFF", "maxColor": "#007BFF"},
            "legend": {
                "align": "right",
                "layout": "vertical",
                "margin": 0,
                "verticalAlign": "top",
                "y": 25,
                "symbolHeight": 280,
            },
            "tooltip": {
                "pointFormat": "Predicted Discount Frequency: <b>{point.value}</b>"
            },
            "series": [
                {
                    "name": "Predicted Discount Frequency",
                    "borderWidth": 1,
                    "data": prediction_heatmap_data,
                    "dataLabels": {
                        "enabled": True,
                        "color": "#000000",
                        "format": "{point.value}",
                    },
                }
            ],
        }

        return original_chart_config, prediction_chart_config

    def generate_html(self, output_file="heatmap_chart.html"):
        original_chart_config, prediction_chart_config = self.generate_chart_config()
        original_chart_json = json.dumps(original_chart_config)
        prediction_chart_json = json.dumps(prediction_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Heatmap Chart - Discount Frequency Analysis</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/modules/heatmap.js"></script>
            <script src="https://code.highcharts.com/modules/exporting.js"></script>
        <style>
            @font-face {{
                    font-family: 'MyCustomFont';
                    src: url('../FVF_Fernando_08.ttf') format('truetype');
                    font-weight: normal;
                    font-style: normal;
                }}

                body {{
                    font-family: 'MyCustomFont', sans-serif;
                }}
            ::-webkit-scrollbar {{
                            width: 12px;
                            background: black;
                            margin: 15px 0 15px 0;
                            border-radius: 0px;
                        }}

                        /* Style cho tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb {{
                            background-color: white;
                            min-height: 30px;
                            border-radius: 7px;
                            border: 3px solid black;
                        }}

                        /* Hover trên tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:hover {{
                            background-color: silver;
                        }}

                        /* Nhấn tay cầm thanh cuộn dọc */
                        ::-webkit-scrollbar-thumb:active {{
                            background-color: rgb(185, 0, 92);
                        }}

                        /* Style cho nút cuộn lên */
                        ::-webkit-scrollbar-button:vertical:increment {{
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-top-left-radius: 7px;
                            border-top-right-radius: 7px;
                        }}

                        /* Style cho nút cuộn xuống */
                        ::-webkit-scrollbar-button:vertical:decrement {{
                            border: 3px solid black;
                            background-color: white;
                            height: 15px;
                            border-bottom-left-radius: 7px;
                            border-bottom-right-radius: 7px;
                        }}

                        /* Ẩn các mũi tên */
                        ::-webkit-scrollbar-button {{
                            background: none;
                        }}

                        /* Cấm các phần trang (khu vực không phải tay cầm) */
                        ::-webkit-scrollbar-track-piece {{
                            background: none;
                        }}
        </style>
        </head>
        <body>
            <div id="container1" style="width: 100%; height: 500px; margin-bottom: 50px;"></div>
            <div id="container2" style="width: 100%; height: 500px;"></div>
            <script type="text/javascript">
                function syncExtremes(e) {{
                    var thisChart = this.chart;

                    if (e.trigger !== 'syncExtremes') {{ // Prevent feedback loop
                        Highcharts.each(Highcharts.charts, function (chart) {{
                            if (chart !== thisChart) {{
                                if (chart.xAxis[0].setExtremes) {{ // It is null while updating
                                    chart.xAxis[0].setExtremes(
                                        e.min,
                                        e.max,
                                        undefined,
                                        false,
                                        {{ trigger: 'syncExtremes' }}
                                    );
                                }}
                            }}
                        }});
                    }}
                }}

                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {original_chart_json};
                    var chartConfig2 = {prediction_chart_json};

                    chartConfig1.chart.events = {{
                        load: function () {{
                            this.xAxis[0].update({{ events: {{ afterSetExtremes: syncExtremes }} }});
                        }}
                    }};
                    chartConfig2.chart.events = {{
                        load: function () {{
                            this.xAxis[0].update({{ events: {{ afterSetExtremes: syncExtremes }} }});
                        }}
                    }};

                    Highcharts.chart('container1', chartConfig1);
                    Highcharts.chart('container2', chartConfig2);
                }});
            </script>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(html_template)

        print(f"Chart has been saved to {output_file}")


# Sử dụng GameDealFetcher và DiscountFrequencyHeatmap để tạo biểu đồ Heatmap
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo DiscountFrequencyHeatmap để tạo biểu đồ
    heatmap_chart = DiscountFrequencyHeatmap(formatted_data)
    heatmap_chart.generate_html(
        "heatmap_chart.html"
    )  # Tạo file HTML với biểu đồ Heatmap


if __name__ == "__main__":
    main()
