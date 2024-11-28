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
        """
        Khởi tạo đối tượng GameDealFetcher với các tham số cấu hình để lấy dữ liệu từ API.
        
        :param api_key: Khóa API để truy cập vào dịch vụ.
        :param game_id: ID của trò chơi cần lấy dữ liệu.
        :param shops_file: Đường dẫn tới tệp JSON chứa thông tin các cửa hàng.
        :param country: Quốc gia mà người dùng muốn lấy dữ liệu, mặc định là "US".
        :param shops: Danh sách các cửa hàng mà người dùng muốn lấy thông tin, mặc định là "61,35,16,6,20,24,37".
        :param since: Thời gian bắt đầu để lấy dữ liệu, mặc định là "2023-11-06T00:00:00Z".
        """
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
        """
        Tải dữ liệu cửa hàng từ tệp JSON.

        :param shops_file: Đường dẫn tới tệp JSON chứa thông tin các cửa hàng.
        :return: Dữ liệu cửa hàng dưới dạng từ điển.
        """
        try:
            with open(shops_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Lỗi khi đọc tệp JSON cửa hàng: {str(e)}")

    def fetch_deal_history(self) -> Union[List, Dict]:
        """
        Lấy lịch sử giảm giá từ API.

        :return: Dữ liệu lịch sử giảm giá (dạng danh sách hoặc từ điển).
        """
        response = requests.get(self.base_url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Lỗi: {response.status_code} - {response.text}")

    def format_data(self, data: Union[List, Dict]) -> List[Dict]:
        """
        Định dạng dữ liệu từ API thành cấu trúc có tổ chức hơn để dễ xử lý.

        :param data: Dữ liệu từ API trả về (dạng danh sách hoặc từ điển).
        :return: Dữ liệu đã được định dạng dưới dạng danh sách các từ điển.
        """
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        formatted_data = []

        for item in data:
            shop_id = str(item["shop"]["id"])
            shop_name = self.shops_data.get(shop_id, "Cửa hàng không xác định")
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


# Class PriceComparisonGroupedBarChart để tạo biểu đồ cột nhóm
class PriceComparisonGroupedBarChart:
    def __init__(self, shops_data: List[Dict]):
        """
        Khởi tạo đối tượng PriceComparisonGroupedBarChart với dữ liệu các cửa hàng.

        :param shops_data: Dữ liệu các cửa hàng đã được định dạng.
        """
        self.shops_data = shops_data

    def process_raw_data(self) -> List[Dict]:
        """
        Xử lý dữ liệu thô để tạo dữ liệu cho biểu đồ cột nhóm.

        :return: Dữ liệu đã xử lý, dạng danh sách các từ điển chứa thông tin giá và thời gian.
        """
        all_dates = set()
        for shop in self.shops_data:
            for deal in shop["deals"]:
                date = deal["timestamp"].split("T")[0][:7]  # Lấy chỉ phần năm và tháng
                all_dates.add(date)

        # Tạo danh sách tất cả các tháng từ tháng đầu tiên đến tháng cuối cùng
        all_dates = (
            pd.date_range(start=min(all_dates), end=max(all_dates), freq="MS")
            .strftime("%Y-%m")
            .tolist()
        )

        latest_prices = {}
        time_point_data = defaultdict(dict)

        for date in all_dates:
            for shop in self.shops_data:
                shop_id = shop["shop_id"]
                shop_title = shop["shop_title"]

                relevant_deals = [
                    deal
                    for deal in shop["deals"]
                    if deal["timestamp"].split("T")[0][:7] <= date
                ]
                if relevant_deals:
                    latest_deal = sorted(relevant_deals, key=lambda x: x["timestamp"])[-1]
                    latest_prices[shop_id] = latest_deal["price"]

                if shop_id in latest_prices:
                    time_point_data[date][shop_title] = latest_prices[shop_id]

        formatted_data = []
        for date, prices in time_point_data.items():
            formatted_data.append({"time_point": date, "prices": prices})

        return formatted_data

    def predict_next_twelve_months(self, processed_data: List[Dict]) -> List[Dict]:
        """
        Dự đoán giá trong 12 tháng tiếp theo dựa trên dữ liệu đã xử lý.

        :param processed_data: Dữ liệu đã xử lý cho biểu đồ cột nhóm.
        :return: Dữ liệu dự đoán giá cho 12 tháng tiếp theo.
        """
        all_dates = pd.to_datetime([entry["time_point"] for entry in processed_data])
        next_twelve_months = [
            (all_dates[-1] + pd.DateOffset(months=i)).strftime("%Y-%m")
            for i in range(1, 13)
        ]

        shop_names = sorted(
            {shop for entry in processed_data for shop in entry["prices"].keys()}
        )
        predictions = []

        for shop_name in shop_names:
            shop_prices = [
                entry["prices"].get(shop_name, None)
                for entry in processed_data
                if entry["prices"].get(shop_name) is not None
            ]

            if len(shop_prices) > 1:
                x = np.arange(len(shop_prices)).reshape(-1, 1)
                y = np.array(shop_prices)
                model = LinearRegression().fit(x, y)
                future_x = np.arange(len(shop_prices), len(shop_prices) + 12).reshape(-1, 1)
                predicted_values = model.predict(future_x)

                for i, date in enumerate(next_twelve_months):
                    predictions.append(
                        {
                            "time_point": date,
                            "shop_name": shop_name,
                            "predicted_price": round(max(0, float(predicted_values[i])), 2),
                        }
                    )

        formatted_predictions = defaultdict(dict)
        for prediction in predictions:
            formatted_predictions[prediction["time_point"]][prediction["shop_name"]] = (
                prediction["predicted_price"]
            )

        formatted_data = [
            {"time_point": date, "prices": formatted_predictions[date]}
            for date in next_twelve_months
        ]
        return formatted_data

    def generate_chart_config(self):
        """
        Tạo cấu hình cho hai biểu đồ cột nhóm: một cho dữ liệu gốc và một cho dữ liệu dự đoán.

        :return: Cấu hình biểu đồ cho dữ liệu gốc và dự đoán.
        """
        processed_data = self.process_raw_data()

        # Dữ liệu gốc cho Biểu đồ cột nhóm
        time_points = [entry["time_point"] for entry in processed_data]
        shop_names = sorted(
            {shop for entry in processed_data for shop in entry["prices"].keys()}
        )
        series = []

        for shop_name in shop_names:
            shop_prices = [
                entry["prices"].get(shop_name, None) for entry in processed_data
            ]
            series.append({"name": shop_name, "data": shop_prices})

        original_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "So sánh giá tại cùng thời điểm cho mỗi cửa hàng (Hàng tháng)",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
            "series": series,
        }

        # Dữ liệu dự đoán cho 12 tháng tiếp theo
        predicted_data = self.predict_next_twelve_months(processed_data)
        predicted_time_points = [entry["time_point"] for entry in predicted_data]
        prediction_series = []

        for shop_name in shop_names:
            predicted_prices = [
                entry["prices"].get(shop_name, None) for entry in predicted_data
            ]
            prediction_series.append({"name": shop_name, "data": predicted_prices})

        prediction_chart_config = {
            "chart": {
                "type": "column",
                "zoomType": "x",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "title": {
                "text": "Dự đoán so sánh giá cho 12 tháng tiếp theo",
                "style": {"fontFamily": "MyCustomFont, sans-serif"},
            },
            "xAxis": {
                "categories": predicted_time_points,
                "title": {
                    "text": "Tháng",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                },
                "labels": {"rotation": -45},
            },
            "yAxis": {
                "title": {
                    "text": "Giá (USD)",
                    "style": {"fontFamily": "MyCustomFont, sans-serif"},
                }
            },
            "tooltip": {
                "shared": True,
                "useHTML": True,
                "headerFormat": "<em>Tháng: {point.key}</em><br/>",
            },
            "series": prediction_series,
        }

        return original_chart_config, prediction_chart_config

    def generate_html(self, output_file="grouped_bar_chart.html"):
        """
        Tạo và lưu file HTML với hai biểu đồ cột nhóm.

        :param output_file: Đường dẫn đến tệp HTML sẽ được tạo ra, mặc định là "grouped_bar_chart.html".
        """
        original_chart_config, prediction_chart_config = self.generate_chart_config()
        original_chart_json = json.dumps(original_chart_config)
        prediction_chart_json = json.dumps(prediction_chart_config)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Biểu đồ cột nhóm - So sánh giá với dự đoán</title>
            <script src="https://code.highcharts.com/highcharts.js"></script>
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

                    if (e.trigger !== 'syncExtremes') {{
                        Highcharts.each(Highcharts.charts, function (chart) {{
                            if (chart !== thisChart) {{
                                if (chart.xAxis[0].setExtremes) {{
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

        print(f"Biểu đồ đã được lưu vào {output_file}")


# Use GameDealFetcher and PriceComparisonGroupedBarChart to generate the chart
def main():
    # Necessary Information
    api_key = "07b0e806aacf15f38b230a850b424b2542dd71af"
    game_id = "018d937f-590c-728b-ac35-38bcff85f086"
    shops_file = "DiscountFrequencyAnalysis/shops.json"

    # Initialize GameDealFetcher to fetch data from API
    fetcher = GameDealFetcher(api_key, game_id, shops_file)
    raw_data = fetcher.fetch_deal_history()
    formatted_data = fetcher.format_data(raw_data)

    # Initialize PriceComparisonGroupedBarChart to generate chart
    grouped_bar_chart = PriceComparisonGroupedBarChart(formatted_data)
    grouped_bar_chart.generate_html(
        "grouped_bar_chart.html"
    )  # Create HTML file with Grouped Bar Chart


if __name__ == "__main__":
    main()
