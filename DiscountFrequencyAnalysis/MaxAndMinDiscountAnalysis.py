import json
import requests
import datetime
from typing import Dict, List, Union
import numpy as np
from sklearn.linear_model import LinearRegression


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


# Class MaximumMinimumDiscountBoxPlot để tạo biểu đồ Box Plot
class MaximumMinimumDiscountBoxPlot:
    def __init__(self, shops_data: List[Dict]):
        self.shops_data = shops_data

    def process_raw_data(self, raw_data: List[Dict]) -> None:
        self.shops_data = []
        for shop in raw_data:
            shop_title = shop.get("shop_title", "Unknown Shop")
            deals = shop.get("deals", [])
            discounts = [round(deal["cut"],2) for deal in deals if "cut" in deal]

            self.shops_data.append({"shop_title": shop_title, "discounts": discounts})

    def predict_next_twelve_months(self):
        predicted_data = []
        for shop in self.shops_data:
            discounts = shop["discounts"]
            if len(discounts) > 1:
                # Using linear regression to predict future discounts
                x = np.arange(len(discounts)).reshape(-1, 1)
                y = np.array(discounts)
                model = LinearRegression().fit(x, y)
                future_x = np.arange(len(discounts), len(discounts) + 12).reshape(-1, 1)
                predicted_values = model.predict(future_x)
                predicted_values = [
                        round(max(0, val),2) for val in predicted_values
                ]  # Ensure no negative predictions

                predicted_data.append(
                    {"shop_title": shop["shop_title"], "discounts": predicted_values}
                )
            else:
                # Not enough data to predict
                predicted_data.append(
                    {"shop_title": shop["shop_title"], "discounts": [0] * 12}
                )

        return predicted_data

    def generate_chart_config(self, title: str, shop_data: List[Dict]):
        categories = []
        data = []
        outliers = []
        mean_values = []

        for index, shop in enumerate(shop_data):
            categories.append(shop["shop_title"])
            discounts = shop["discounts"]

            if len(discounts) > 0:
                min_discount = min(discounts)
                max_discount = max(discounts)
                lower_quartile = self._calculate_percentile(discounts, 25)
                median = self._calculate_percentile(discounts, 50)
                upper_quartile = self._calculate_percentile(discounts, 75)
                mean_value = sum(discounts) / len(discounts)
                data.append(
                    [min_discount, lower_quartile, median, upper_quartile, max_discount]
                )
                mean_values.append([index, mean_value])

                # Identify outliers
                for value in discounts:
                    if value < lower_quartile - 1.5 * (
                        upper_quartile - lower_quartile
                    ) or value > upper_quartile + 1.5 * (
                        upper_quartile - lower_quartile
                    ):
                        outliers.append([index, value])
            else:
                # Nếu không có dữ liệu giảm giá, thêm giá trị mặc định
                data.append([0, 0, 0, 0, 0])

        chart_config = {
            "chart": {"type": "boxplot", "style": {"fontFamily": "MyCustomFont"}},
            "title": {"text": title, "style": {"fontFamily": "MyCustomFont"}},
            "xAxis": {"categories": categories, "title": {"text": "Shops"}},
            "yAxis": {"title": {"text": "Discount (%)"}},
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Shop: {point.key}</em><br/>",
            },
            "series": [
                {
                    "name": "Discount Distribution",
                    "data": data,
                    "tooltip": {
                        "headerFormat": "<em>Discount Distribution for {point.key}</em><br/>"
                    },
                },
                {
                    "name": "Outliers",
                    "type": "scatter",
                    "data": outliers,
                    "marker": {
                        "fillColor": "rgba(223, 83, 83, .5)",
                        "lineWidth": 1,
                        "lineColor": "rgba(223, 83, 83, 1)",
                    },
                    "tooltip": {"pointFormat": "Outlier: {point.y}%<br/>"},
                },
                {
                    "name": "Theoretical Mean",
                    "type": "scatter",
                    "data": mean_values,
                    "marker": {
                        "fillColor": "rgba(0, 100, 0, .5)",
                        "lineWidth": 1,
                        "lineColor": "rgba(0, 100, 0, 1)",
                        "radius": 5,
                    },
                    "tooltip": {"pointFormat": "Theoretical Mean: {point.y:.2f}%<br/>"},
                },
            ],
        }

        return chart_config

    @staticmethod
    def _calculate_percentile(data, percentile):
        size = len(data)
        sorted_data = sorted(data)
        index = int(round(percentile / 100.0 * (size - 1)))
        return sorted_data[index]

    def generate_html(self, output_file="boxplot_chart.html"):
        # Generate original data chart
        original_chart_config = self.generate_chart_config(
            "Phân Tích Giảm Giá Tối Đa và Tối Thiểu Cho Mỗi Cửa Hàng (Lịch Sử)",
            self.shops_data,
        )
        original_chart_json = json.dumps(original_chart_config)

        # Generate predicted data chart
        predicted_shops_data = self.predict_next_twelve_months()
        predicted_chart_config = self.generate_chart_config(
            "Dự Đoán Phân Tích Giảm Giá Tối Đa và Tối Thiểu Cho Mỗi Cửa Hàng (12 Tháng Tới)",
            predicted_shops_data,
        )
        predicted_chart_json = json.dumps(predicted_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Box Plot Chart with Predictions</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
            <script src="https://code.highcharts.com/highcharts-more.js"></script>
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
                document.addEventListener('DOMContentLoaded', function () {{
                    var chartConfig1 = {original_chart_json};
                    var chartConfig2 = {predicted_chart_json};

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


# Sử dụng GameDealFetcher và MaximumMinimumDiscountBoxPlot để tạo biểu đồ
def main():
    # Các thông tin cần thiết
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Khởi tạo GameDealFetcher để lấy dữ liệu từ API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Khởi tạo MaximumMinimumDiscountBoxPlot để tạo biểu đồ
    box_plot_chart = MaximumMinimumDiscountBoxPlot([])
    box_plot_chart.process_raw_data(
        formatted_data
    )  # Sử dụng dữ liệu từ GameDealFetcher
    box_plot_chart.generate_html(
        "boxplot_chart.html"
    )  # Tạo file HTML với biểu đồ Box Plot


if __name__ == "__main__":
    main()
